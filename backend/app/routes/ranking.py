from flask import Blueprint, jsonify, request
from app.repositories import entity_repository as repo
from app.utils.serializers import serialize_entity
import asyncio

ranking_bp = Blueprint("ranking", __name__)

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@ranking_bp.route("/", methods=["GET"])
def get_ranking():
    """
    GET /api/ranking/
    Retorna o ranking atual ordenado por score decrescente.

    Query params:
        - page      (int, default=1)
        - page_size (int, default=20, max=20)
    """
    try:
        page      = max(1, int(request.args.get("page", 1)))
        page_size = min(20, max(1, int(request.args.get("page_size", 20))))
    except ValueError:
        return jsonify({"error": "Parâmetros de paginação inválidos"}), 400

    entities = run_async(repo.get_all(page=page, page_size=page_size))
    total    = run_async(repo.count_entities())

    ranking = [
        serialize_entity(entity, position=i + 1 + (page - 1) * page_size)
        for i, entity in enumerate(entities)
    ]

    return jsonify({
        "data": ranking,
        "meta": {
            "page":       page,
            "page_size":  page_size,
            "total":      total,
            "total_pages": -(-total // page_size),  # ceil division
        }
    }), 200

@ranking_bp.route("/<int:entity_id>", methods=["GET"])
def get_entity(entity_id: int):
    """
    GET /api/ranking/<entity_id>
    Retorna os dados de uma entidade específica.
    """
    entity = run_async(repo.get_by_id(entity_id))

    if not entity:
        return jsonify({"error": f"Entidade {entity_id} não encontrada"}), 404

    return jsonify({"data": serialize_entity(entity, position=0)}), 200

@ranking_bp.route("/reset", methods=["POST"])
def reset_ranking():
    """
    POST /api/ranking/reset
    Zera todos os scores. Requer header: X-Secret-Key
    """
    from app.routes.ranking_reset import handle_reset
    return handle_reset()