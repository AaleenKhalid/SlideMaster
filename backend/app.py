from flask import Flask
from flask_cors import CORS
from backend.routes.slide_routes import slide_bp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],  # Svelte dev server
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Register blueprints
    app.register_blueprint(slide_bp, url_prefix='/api/slides')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)