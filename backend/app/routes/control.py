from flask import Blueprint, jsonify, request

control_bp = Blueprint("control", __name__)

@control_bp.route("/start", methods=["POST"])
async def start_live():
    """Inicia a conexão com a live do TikTok."""
    return jsonify({"message": "start endpoint ok"})

@control_bp.route("/stop", methods=["POST"])
async def stop_live():
    """Encerra a conexão com a live do TikTok."""
    return jsonify({"message": "stop endpoint ok"})

@control_bp.route("/status", methods=["GET"])
async def live_status():
    """Retorna o status atual da conexão com a live."""
    return jsonify({"connected": False, "username": None})