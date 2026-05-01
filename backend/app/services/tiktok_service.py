import threading
import asyncio
from typing import Optional

from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    GiftEvent,
    LiveEndEvent
)

from app.services.logger import get_logger
from app.repositories import entity_repository as entity_repo
from app.repositories import gift_repository as gift_repo

logger = get_logger("tiktok_service")

class TikTokServiceState:
    def __init__(self):
        self.connected:      bool          = False
        self.username:       Optional[str] = None
        self.last_error:     Optional[str] = None
        self.gifts_received: int           = 0

    def reset(self, username: Optional[str] = None):
        self.connected      = False
        self.username       = username
        self.last_error     = None
        self.gifts_received = 0

class TikTokLiveService:
    def __init__(self, socketio=None):
        self.socketio    = socketio
        self.state       = TikTokServiceState()
        self._client:    Optional[TikTokLiveClient] = None
        self._thread:    Optional[threading.Thread] = None

    # Handlers de Eventos
    async def _on_connect(self, event: ConnectEvent):
        self.state.connected = True
        self.state.last_error = None
        logger.info(f"✅ Monitoramento Ativo: @{event.unique_id}")
        self._emit_socket("connection_status", {"connected": True, "username": self.state.username})

    async def _on_disconnect(self, event: DisconnectEvent):
        self.state.connected = False
        logger.warning(f"⚠️ Conexão encerrada com @{self.state.username}.")
        self._emit_socket("connection_status", {"connected": False})

    async def _on_gift(self, event: GiftEvent):
        try:
            if event.gift.type == 1 and event.streaking:
                return 

            quantity = event.repeat_count or 1
            self.state.gifts_received += 1
            
            asyncio.create_task(self._process_gift_db(
                event.gift.id, 
                event.gift.name, 
                event.user.unique_id, 
                quantity
            ))
        except Exception as e:
            logger.error(f"Erro GiftEvent: {e}")

    async def _process_gift_db(self, gift_id, gift_name, sender, qty):
        try:
            gift_db = await gift_repo.get_by_tiktok_gift_id(gift_id)
            if gift_db and gift_db.gift_map:
                entity = gift_db.gift_map[0].entity
                points = gift_db.point_value * qty
                updated = await entity_repo.update_score(entity.id, points)
                
                logger.info(f"🎁 {sender} -> {gift_name} (x{qty}) | +{points} pts para {entity.name}")
                
                self._emit_socket("score_update", {
                    "entity_id": entity.id, 
                    "new_score": updated.total_score, 
                    "gift_name": gift_name, 
                    "sender": sender
                })
        except Exception as e:
            logger.error(f"Erro DB Update: {e}")

    def _emit_socket(self, event: str, data: dict):
        if self.socketio:
            self.socketio.emit(event, data)

    # Motor Principal
    def _thread_main(self, username: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            formatted_username = username if username.startswith('@') else f"@{username}"
            self._client = TikTokLiveClient(unique_id=formatted_username)

            self._client.on(ConnectEvent,    self._on_connect)
            self._client.on(DisconnectEvent, self._on_disconnect)
            self._client.on(GiftEvent,       self._on_gift)
            self._client.on(LiveEndEvent,    lambda e: logger.info("📢 Live encerrada."))
            
            self._client.run()
            
        except Exception as e:
            self.state.last_error = str(e)
            logger.error(f"Erro crítico na thread: {e}")
        finally:
            self.state.connected = False
            self._client = None
            try:
                loop.stop()
                loop.close()
            except:
                pass
            logger.info(f"🏁 Thread de @{username} finalizada.")

    # Interface Pública
    def start(self, username: str) -> dict:
        if self._thread and self._thread.is_alive():
            if self.state.connected:
                return {"success": False, "message": "Serviço já ativo."}
            
            # Limpeza preventiva se a thread anterior estiver em encerramento
            self._thread.join(timeout=1.0)
            self._thread = None
            
        self.state.reset(username)
        self._thread = threading.Thread(target=self._thread_main, args=(username,), daemon=True)
        self._thread.start()
        return {"success": True, "message": f"Serviço iniciado para @{username}.", "username": f"@{username}"}

    def stop(self) -> dict:
        """Encerra a conexão e força a limpeza da referência da thread."""
        if not self._client and (not self._thread or not self._thread.is_alive()):
            return {"success": False, "message": "Nenhum serviço ativo para parar."}

        try:
            if self._client:
                self._client.disconnect()
            
            self.state.connected = False
            
            # Aguarda a finalização real para evitar threads zumbis no status
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)
            
            # Força a nulidade da referência para que o status retorne false imediatamente
            self._thread = None 
            return {"success": True, "message": "Serviço encerrado com sucesso."}
            
        except Exception as e:
            logger.error(f"Erro ao parar: {e}")
            self._thread = None
            return {"success": False, "message": f"Erro ao parar: {e}"}

    def get_status(self) -> dict:
        # Verifica se a thread existe e está ativa
        is_alive = self._thread.is_alive() if self._thread is not None else False
        return {
            "connected":      self.state.connected,
            "username":       self.state.username,
            "gifts_received": self.state.gifts_received,
            "last_error":     self.state.last_error,
            "thread_alive":   is_alive
        }

tiktok_service = TikTokLiveService()