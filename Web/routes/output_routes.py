from flask import Blueprint, current_app, send_file
from pathlib import Path

output_bp = Blueprint("output", __name__)

@output_bp.route("/download/<filename>")
def download(filename):
    file_path = Path(current_app.config["OUTPUT_FOLDER"]) / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404
