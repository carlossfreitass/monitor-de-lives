from flask_socketio import Namespace, emit
from app.services.logger import get_logger
import time

logger = get_logger("socket.ranking")

# Tempo mínimo entre broadcasts
THROTTLE_INTERVAL = 0.5

class RankingNamespace(Namespace):
    """
    Permite a conexão com o cliente por meio de eventos.
        - ranking_update  → score atualizado de um time
        - live_status     → estado da conexão com a live
        - error_alert     → erros tratados
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_emit: float = 0.0
        self._pending:   dict | None = None

    # Handlers de conexão
    def on_connect(self):
        logger.info("🔌 Cliente conectado ao namespace /ranking")
        # Envia o status atual da live assim que o cliente conecta
        from app.services.tiktok_service import tiktok_service
        status = tiktok_service.get_status()
        emit("live_status", {
            "connected": status["connected"],
            "username":  status["username"],
        })

    def on_disconnect(self):
        logger.info("🔌 Cliente desconectado do namespace /ranking")

    # Emissores Públicos
    def emit_score_update(self, payload: dict) -> None:
        """
        Emite ranking_update
        """
        now = time.monotonic()
        elapsed = now - self._last_emit

        if elapsed >= THROTTLE_INTERVAL:
            self._broadcast_score(payload)
        else:
            self._pending = payload
            delay = THROTTLE_INTERVAL - elapsed
            self._schedule_pending(delay)

    def emit_live_status(self, connected: bool, username: str | None) -> None:
        """Broadcast do estado da live para todos os clientes."""
        from app import socketio
        socketio.emit(
            "live_status",
            {"connected": connected, "username": username},
            namespace="/ranking",
        )
        logger.info(f"📡 live_status emitido → connected={connected}")

    def emit_error_alert(self, code: str, message: str) -> None:
        """Broadcast de erro tratado para todos os clientes."""
        from app import socketio
        socketio.emit(
            "error_alert",
            {"code": code, "message": message},
            namespace="/ranking",
        )
        logger.warning(f"🚨 error_alert emitido → [{code}] {message}")

    # Emissores Internos
    def _broadcast_score(self, payload: dict) -> None:
        """Emite ranking_update e atualiza o timestamp."""
        from app import socketio
        socketio.emit("ranking_update", payload, namespace="/ranking")
        self._last_emit = time.monotonic()
        self._pending = None
        logger.debug(
            f"📡 ranking_update → {payload.get('entity_name')} "
            f"score={payload.get('new_score')}"
        )

    def _schedule_pending(self, delay: float) -> None:
        import threading
        timer = threading.Timer(delay, self._flush_pending)
        timer.daemon = True
        timer.start()

    def _flush_pending(self) -> None:
        """Envia o payload pendente se ainda existir."""
        if self._pending is not None:
            self._broadcast_score(self._pending)

# Singleton
ranking_namespace = RankingNamespace("/ranking")