from .transcribe_routes import transcribe_bp
from .download_routes import download_bp
from .output_routes import output_bp

def register_blueprints(app):
    app.register_blueprint(transcribe_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(output_bp)
