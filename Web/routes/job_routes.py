from flask import Blueprint, jsonify
from progress import progress_store, job_results

job_bp = Blueprint("job", __name__, url_prefix="/job")

@job_bp.route("/progress/<job_id>")
def get_progress(job_id):
    progress = progress_store.get(job_id)
    if progress is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"progress": progress})

@job_bp.route("/result/<job_id>")
def get_result(job_id):
    job = job_results.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["transcript"] is None:
        return jsonify({"error": "Transcript not ready"}), 202

    return jsonify({
        "transcript": job["transcript"],
        "download_txt": job["output_txt"].name,
        "download_srt": job["output_srt"].name
    })
