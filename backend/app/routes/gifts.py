from flask import Blueprint, jsonify

gifts_bp = Blueprint("gifts", __name__)

@gifts_bp.route("/", methods=["GET"])
async def get_gifts():
    """Retorna o mapa de presentes cadastrados."""
    return jsonify({"message": "gifts endpoint ok", "data": []})