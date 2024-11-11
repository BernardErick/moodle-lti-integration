from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importando e registrando qualquer rota que for criada!!
    from .routes import main
    app.register_blueprint(main)

    return app