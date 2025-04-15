from pathlib import Path
from uuid import uuid4
from flask import current_app
from transcriber import Transcriber


def prepare_file_paths(file):
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    output_dir = Path(current_app.config["OUTPUT_FOLDER"])
    temp_dir = Path(current_app.config["TEMP_FOLDER"])

    for d in [upload_dir, output_dir, temp_dir]:
        d.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix
    uid = uuid4()

    input_path = upload_dir / f"input_{uid}{file_ext}"
    output_txt = output_dir / f"output_{uid}.txt"
    output_srt = output_txt.with_suffix(".srt")

    return input_path, output_txt, output_srt

def create_transcriber(input_path, output_txt, lang, model, update_progress):
    temp_dir = Path(current_app.config["TEMP_FOLDER"])
    return Transcriber(
        video_path=input_path,
        output_path=output_txt,
        lang=lang,
        model=model,
        chunk=60,
        keep_temp=False,
        update_status=lambda msg: print(msg),
        update_progress=update_progress,
        temp_folder=temp_dir
    )
