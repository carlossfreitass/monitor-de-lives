from flask import Blueprint, jsonify, request
from app.services.tiktok_service import tiktok_service
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
        return jsonify({"error": "Campo 'username' é obrigatório."}), 400

    # Injeta o socketio no serviço na primeira chamada
    if tiktok_service.socketio is None:
        from app import socketio
        tiktok_service.socketio = socketio

    result = tiktok_service.start(username)
    status = 200 if result["success"] else 409

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

    return jsonify(result), status

@control_bp.route("/status", methods=["GET"])
def live_status():
    """
    GET /api/control/status
    Retorna o estado atual do serviço.
    """
    return jsonify(tiktok_service.get_status()), 200