# /app/__init__.py
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from .models.user import User


import redis

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.client import Redis
    app: 'Flask & Redis'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

    # Configuración de Redis
    app.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes.discovery import discovery as discovery_blueprint
    app.register_blueprint(discovery_blueprint, url_prefix='/discovery')

    from app.routes.creations import creations
    app.register_blueprint(creations, url_prefix='/creations')
    from .routes.favorites import favorites
    from .routes.auth import auth
    app.register_blueprint(favorites, url_prefix='/favorites')
    app.register_blueprint(auth, url_prefix='/auth')

    # Redirigir la ruta principal a 'discovery'
    @app.route('/')
    def index():
        return redirect(url_for('discovery.show_feed'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_user(user_id)

    return app