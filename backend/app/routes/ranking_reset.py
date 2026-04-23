from flask import request, jsonify
from app.repositories import entity_repository as repo
import asyncio
import os

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def _check_auth() -> bool:
    """
    Valida o header X-Secret-Key contra a SECRET_KEY do .env.
    Retorna True se autorizado.
    """
    secret      = os.getenv("SECRET_KEY", "")
    provided    = request.headers.get("X-Secret-Key", "")

    if not secret:
        return False

    # Comparação segura contra timing attacks
    import hmac
    return hmac.compare_digest(secret, provided)

def handle_reset():
    """
    POST /api/ranking/reset
    Zera todos os scores do ranking.

    Headers obrigatórios:
        X-Secret-Key: <valor do SECRET_KEY no .env>

    Body opcional (JSON):
        { "confirm": true }   ← segurança extra
    """
    # 1. Autenticação
    if not _check_auth():
        return jsonify({
            "error": "Não autorizado. Header X-Secret-Key inválido ou ausente."
        }), 401

    # 2. Confirmação no body
    body    = request.get_json(silent=True) or {}
    confirm = body.get("confirm", False)

    if not confirm:
        return jsonify({
            "error": "Confirmação necessária. Envie { \"confirm\": true } no body."
        }), 400

    # 3. Executa o reset
    try:
        updated = run_async(repo.reset_all_scores())
        return jsonify({
            "message":  f"Ranking zerado com sucesso.",
            "updated":  updated,
        }), 200

    except Exception as e:
        return jsonify({
            "error":   "Erro interno ao zerar o ranking.",
            "detail":  str(e)
        }), 500