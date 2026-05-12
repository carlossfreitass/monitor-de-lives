from flask import Blueprint, jsonify, request
from app.services.tiktok_service import tiktok_service
from app.sockets.ranking_namespace import ranking_namespace
import os, hmac

control_bp = Blueprint("control", __name__)

def _check_auth() -> bool:
    secret   = os.getenv("SECRET_KEY", "")
    provided = request.headers.get("X-Secret-Key", "")
    if not secret:
        return False
    return hmac.compare_digest(secret, provided)

@control_bp.route("/start", methods=["POST"])
def start_live():
    """
    POST /api/control/start
    Inicia a conexão com a live do TikTok.
    """
    if not _check_auth():
        return jsonify({"error": "Não autorizado."}), 401

    body     = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()

    if not username:
        ranking_namespace.emit_error_alert(
            code="INVALID_USERNAME",
            message="Username não informado na requisição de start.",
        )
        return jsonify({"error": "Campo 'username' é obrigatório."}), 400

    result = tiktok_service.start(username)
    status = 200 if result["success"] else 409

    if not result["success"]:
        ranking_namespace.emit_error_alert(
            code="START_FAILED",
            message=result["message"],
        )

    return jsonify(result), status

@control_bp.route("/stop", methods=["POST"])
def stop_live():
    """
    POST /api/control/stop
    Encerra a conexão com a live.
    """
    if not _check_auth():
        return jsonify({"error": "Não autorizado."}), 401

    result = tiktok_service.stop()
    status = 200 if result["success"] else 409

    if result["success"]:
        ranking_namespace.emit_live_status(connected=False, username=None)
    else:
        ranking_namespace.emit_error_alert(
            code="STOP_FAILED",
            message=result["message"],
        )

    return jsonify(result), status

@control_bp.route("/status", methods=["GET"])
def live_status():
    """
    GET /api/control/status
    Retorna o estado atual do serviço.
    """
    return jsonify(tiktok_service.get_status()), 200