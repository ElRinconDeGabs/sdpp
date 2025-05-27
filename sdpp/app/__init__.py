# app/__init__.py
from flask import Flask

def create_app():
    import os
    static_folder_path = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(__name__,
                static_folder=static_folder_path,
                static_url_path='/static')

    # 🔑  Clave de sesión (usa una env-var en producción)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

    from .auth.routes import auth_bp
    from .main.routes import main_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp) 

    return app
