from flask import Blueprint, jsonify, request
from app.repositories import event_repository as repo
from app.services.score_engine import score_engine
import asyncio

events_bp = Blueprint("events", __name__)

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@events_bp.route("/recent", methods=["GET"])
def get_recent_events():
    """
    GET /api/events/recent?limit=50
    Últimos N eventos para debug e auditoria.
    """
    try:
        limit = min(200, max(1, int(request.args.get("limit", 50))))
    except ValueError:
        return jsonify({"error": "Parâmetro 'limit' inválido."}), 400

    events = run_async(repo.get_recent_events(limit=limit))
    total  = run_async(repo.count_events())

    data = [_serialize_event(e) for e in events]

    return jsonify({
        "data":  data,
        "meta": {
            "returned": len(data),
            "total":    total,
            "limit":    limit,
        }
    }), 200

@events_bp.route("/cache", methods=["GET"])
def get_cache_status():
    """
    GET /api/events/cache
    Retorna o estado atual do cache em memória do ScoreEngine.
    """
    snapshot = score_engine.get_cache_snapshot()
    return jsonify({
        "loaded":  bool(snapshot),
        "entries": len(snapshot),
        "cache":   snapshot,
    }), 200

@events_bp.route("/cache/reload", methods=["POST"])
def reload_cache():
    """
    POST /api/events/cache/reload
    Força recarga do gift_map do banco para a memória.
    """
    run_async(score_engine.reload_cache())
    snapshot = score_engine.get_cache_snapshot()
    return jsonify({
        "message": "Cache recarregado com sucesso.",
        "entries": len(snapshot),
    }), 200

#  Serializer
def _serialize_event(event) -> dict:
    return {
        "id":              event.id,
        "tiktok_gift_id":  event.tiktok_gift_id,
        "gift_name":       event.gift_name,
        "sender":          event.sender_username,
        "repeat_count":    event.repeat_count,
        "points_awarded":  event.points_awarded,
        "entity_id":       event.entity_id,
        "entity_name":     event.entity.name if event.entity else None,
        "created_at":      event.created_at.isoformat(),
    }