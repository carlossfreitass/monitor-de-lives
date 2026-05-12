import threading
import asyncio
import json
from typing import Optional

from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    GiftEvent,
    LiveEndEvent
)

from app.services.logger import get_logger
from app.services.score_engine import score_engine
from app.sockets.ranking_namespace import ranking_namespace

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
    def __init__(self):
        self.state    = TikTokServiceState()
        self._client: Optional[TikTokLiveClient] = None
        self._thread: Optional[threading.Thread] = None

    # Handlers de Eventos
    async def _on_connect(self, event: ConnectEvent):
        self.state.connected  = True
        self.state.last_error = None
        logger.info(f"✅ Monitoramento Ativo: @{event.unique_id}")
        ranking_namespace.emit_live_status(
            connected=True,
            username=self.state.username,
        )

    async def _on_disconnect(self, event: DisconnectEvent):
        self.state.connected = False
        logger.warning(f"⚠️ Conexão encerrada com @{self.state.username}.")
        ranking_namespace.emit_live_status(connected=False, username=None)

    async def _on_gift(self, event: GiftEvent):
        try:
            if event.gift.type == 1 and event.streaking:
                return

            quantity = event.repeat_count or 1
            self.state.gifts_received += 1

            raw = json.dumps({
                "gift_id":      event.gift.id,
                "gift_name":    event.gift.name,
                "repeat_count": quantity,
                "sender":       event.user.unique_id,
                "streaking":    event.streaking,
            })

            asyncio.create_task(self._process_gift_db(
                gift_id=event.gift.id,
                gift_name=event.gift.name,
                sender=event.user.unique_id,
                qty=quantity,
                raw_event=raw,
            ))
        except Exception as e:
            logger.error(f"Erro GiftEvent: {e}")

    async def _process_gift_db(self, gift_id, gift_name, sender, qty, raw_event):
        result = await score_engine.process_gift(
            tiktok_gift_id=gift_id,
            gift_name=gift_name,
            sender_username=sender,
            repeat_count=qty,
            raw_event=raw_event,
        )

        if result:
            ranking_namespace.emit_score_update(result)

    # Motor Principal
    def _thread_main(self, username: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(score_engine.load_cache())

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
            ranking_namespace.emit_error_alert(
                code="THREAD_ERROR",
                message=str(e),
            )
        finally:
            self.state.connected = False
            self._client = None

            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            except Exception:
                pass

            asyncio.set_event_loop(None)

            try:
                loop.close()
            except Exception:
                pass

            logger.info(f"🏁 Thread de @{username} finalizada.")

    # Interface Pública
    def start(self, username: str) -> dict:
        if self._thread and self._thread.is_alive():
            if self.state.connected:
                return {"success": False, "message": "Serviço já ativo."}
            self._thread.join(timeout=3.0)
            self._thread = None

        import time
        time.sleep(0.2)

        self.state.reset(username)
        self._thread = threading.Thread(
            target=self._thread_main,
            args=(username,),
            daemon=True,
        )
        self._thread.start()
        return {
            "success":  True,
            "message":  f"Serviço iniciado para @{username}.",
            "username": f"@{username}",
        }

    def stop(self) -> dict:
        if not self._client and (not self._thread or not self._thread.is_alive()):
            return {"success": False, "message": "Nenhum serviço ativo para parar."}

        try:
            if self._client:
                self._client.disconnect()

            self.state.connected = False

            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)

            self._thread = None
            return {"success": True, "message": "Serviço encerrado com sucesso."}

        except Exception as e:
            logger.error(f"Erro ao parar: {e}")
            self._thread = None
            return {"success": False, "message": f"Erro ao parar: {e}"}

    def get_status(self) -> dict:
        is_alive = self._thread.is_alive() if self._thread is not None else False
        return {
            "connected":      self.state.connected,
            "username":       self.state.username,
            "gifts_received": self.state.gifts_received,
            "last_error":     self.state.last_error,
            "thread_alive":   is_alive,
        }

tiktok_service = TikTokLiveService()