from flask import Blueprint, send_file, current_app
from pathlib import Path

download_bp = Blueprint("download", __name__)

@download_bp.route("/download/<filename>")
def download(filename):
    output_dir = Path(current_app.config["OUTPUT_FOLDER"])
    file_path = output_dir / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404
