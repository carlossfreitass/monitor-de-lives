from flask import Blueprint, jsonify

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/", methods=["GET"])
async def get_ranking():
    """Retorna o ranking atual ordenado por score."""
    return jsonify({"message": "ranking endpoint ok", "data": []})