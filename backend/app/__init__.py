from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS  # Adicionado para resolver o erro de Fetch
import asyncio

# Configuração do SocketIO
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading",
    logger=False,
    engineio_logger=False,
)

def create_app():
    app = Flask(__name__)

    # Habilita o CORS para as rotas da API (resolve o erro 'Access-Control-Allow-Origin')
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Carrega configurações
    from app.config import get_config
    app.config.from_object(get_config())

    # Inicializa o SocketIO no App
    socketio.init_app(app)

    # Registra o Namespace do Ranking
    from app.sockets.ranking_namespace import ranking_namespace
    socketio.on_namespace(ranking_namespace)

    # Importação e Registro dos Blueprints (Rotas)
    from app.routes.ranking import ranking_bp
    from app.routes.gifts   import gifts_bp
    from app.routes.control import control_bp
    from app.routes.events  import events_bp

    app.register_blueprint(ranking_bp, url_prefix="/api/ranking")
    app.register_blueprint(gifts_bp,   url_prefix="/api/gifts")
    app.register_blueprint(control_bp, url_prefix="/api/control")
    app.register_blueprint(events_bp,  url_prefix="/api/events")

    # Inicialização do Cache do ScoreEngine
    with app.app_context():
        from app.services.score_engine import score_engine
        try:
            # Cria um loop temporário apenas para carregar o cache no startup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(score_engine.load_cache())
            loop.close()
        except Exception as e:
            import logging
            logging.getLogger("startup").warning(f"❌ Cache não carregado no startup: {e}")

    # Rota de verificação de integridade
    @app.route("/health")
    def health():
        return {"status": "ok", "env": app.config.get("FLASK_ENV", "production")}

    return app