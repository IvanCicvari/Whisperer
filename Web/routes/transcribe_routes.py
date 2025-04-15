from flask import Blueprint, request, jsonify, current_app
from utils.transcribe_utils import prepare_file_paths, create_transcriber
from progress import progress_store, job_results
import threading
import uuid

transcribe_bp = Blueprint("transcribe", __name__)

def transcribe_job(app, job_id, input_path, output_txt, lang, model, update_progress):
    print(f"🧵 Background job started for {job_id}")
    with app.app_context(): 
        transcriber = create_transcriber(input_path, output_txt, lang, model, update_progress)
        transcript = transcriber.transcribe()
        job_results[job_id]["transcript"] = transcript
        print(f"✅ Job {job_id} complete and stored in job_results")


@transcribe_bp.route("/transcribe", methods=["POST"])
def transcribe():
    file = request.files.get("file")
    lang = request.form.get("lang", "hr")
    model = request.form.get("model", "tiny")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    job_id = str(uuid.uuid4())
    progress_store[job_id] = 0.0

    def update_progress(p):
        progress_store[job_id] = round(p, 2)

    input_path, output_txt, output_srt = prepare_file_paths(file)
    file.save(input_path)

    job_results[job_id] = {
        "input_path": input_path,
        "output_txt": output_txt,
        "output_srt": output_srt,
        "lang": lang,
        "model": model,
        "transcript": None,
    }

    # ✅ Get app from current_app
    app_instance = current_app._get_current_object()

    threading.Thread(
        target=transcribe_job,
        args=(app_instance, job_id, input_path, output_txt, lang, model, update_progress),
        daemon=True
    ).start()

    print("✅ Returning job_id immediately:", job_id)
    return jsonify({"job_id": job_id})
