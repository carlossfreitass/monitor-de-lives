from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    # Configuração
    from app.config import get_config
    app.config.from_object(get_config())

    # SocketIO
    socketio.init_app(app)

    # Blueprints
    from app.routes.ranking import ranking_bp
    from app.routes.gifts   import gifts_bp
    from app.routes.control import control_bp

    app.register_blueprint(ranking_bp, url_prefix="/api/ranking")
    app.register_blueprint(gifts_bp,   url_prefix="/api/gifts")
    app.register_blueprint(control_bp, url_prefix="/api/control")

    # Health check
    @app.route("/health")
    def health():
        return {"status": "ok", "env": app.config["FLASK_ENV"]}

    return app