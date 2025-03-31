from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
import uuid
import threading
from transcriber import Transcriber  # ✅ Ovo je točno
from transcriber import Transcriber
from flask import render_template

transcribe_bp = Blueprint("transcribe", __name__)

from flask import Blueprint, request, render_template, current_app, send_file
from pathlib import Path
import uuid
from transcriber import Transcriber

transcribe_bp = Blueprint("transcribe", __name__)

@transcribe_bp.route("/transcribe", methods=["POST"])
def transcribe():
    file = request.files.get("file")
    lang = request.form.get("lang", "hr")
    model = request.form.get("model", "tiny")

    if not file:
        return "No file uploaded", 400

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    output_dir = Path(current_app.config["OUTPUT_FOLDER"])
    temp_dir = Path(current_app.config["TEMP_FOLDER"])

    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix
    input_path = upload_dir / f"input_{uuid.uuid4()}{file_ext}"
    output_txt = output_dir / f"output_{uuid.uuid4()}.txt"
    output_srt = output_txt.with_suffix(".srt")

    file.save(input_path)

    transcriber = Transcriber(
        video_path=input_path,
        output_path=output_txt,
        lang=lang,
        model=model,
        chunk=60,
        keep_temp=False,
        update_status=lambda msg: print(msg),
        update_progress=lambda p: None,
        temp_folder=temp_dir
    )

    transcript = transcriber.transcribe()

    return render_template("index.html",
        transcript=transcript,
        download_txt=output_txt.name,
        download_srt=output_srt.name
    )

