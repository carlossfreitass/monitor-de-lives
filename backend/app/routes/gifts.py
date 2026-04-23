from flask import Blueprint, jsonify
from app.repositories import gift_repository as repo
from app.utils.serializers import serialize_gift_map
import asyncio

gifts_bp = Blueprint("gifts", __name__)

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@gifts_bp.route("/", methods=["GET"])
def get_gifts():
    """
    GET /api/gifts/
    Retorna todos os presentes cadastrados.
    """
    gifts = run_async(repo.get_all_gifts())

    data = [
        {
            "id":              g.id,
            "tiktok_gift_id":  g.tiktok_gift_id,
            "name":            g.name,
            "icon_url":        g.icon_url,
            "point_value":     g.point_value,
        }
        for g in gifts
    ]

    return jsonify({"data": data, "total": len(data)}), 200

@gifts_bp.route("/map", methods=["GET"])
def get_gift_map():
    """
    GET /api/gifts/map
    Retorna o mapeamento completo gift → entidade.
    Usado pelo frontend para exibir qual presente votar por cada time.
    """
    gift_map = run_async(repo.get_gift_map())

    data = [serialize_gift_map(entry) for entry in gift_map]

    # Indexado por tiktok_gift_id para lookup O(1) no frontend
    indexed = {str(entry["tiktok_gift_id"]): entry for entry in data}

    return jsonify({
        "data":    data,
        "indexed": indexed,
        "total":   len(data)
    }), 200