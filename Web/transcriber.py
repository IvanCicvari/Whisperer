import subprocess
import whisper
import shutil
from utils.srt_utils import write_srt
from pathlib import Path
from pydub import AudioSegment
import uuid

class Transcriber:
    def __init__(self, video_path, output_path, lang, model, chunk, keep_temp, update_status, update_progress, temp_folder):
        self.video = Path(video_path)
        self.output = Path(output_path)
        self.lang = lang
        self.model_name = model
        self.chunk_length = chunk
        self.keep_temp = keep_temp
        self.update_status = update_status
        self.update_progress = update_progress
        self.audio_file = Path(temp_folder) / f"temp_{uuid.uuid4().hex}.wav"
        self.chunk_dir = Path(temp_folder) / f"chunks_{uuid.uuid4().hex}"


    def transcribe(self):
        full_transcript = ""

        try:
            self.prepare_audio()
            model, chunks, total_chunks = self.load_model_and_chunks()

            with self.output.open("w", encoding="utf-8") as out_file:
                for i, chunk_path in enumerate(chunks, 1):
                    result = model.transcribe(str(chunk_path), language=self.lang, verbose=False)

                    srt_path = chunk_path.with_suffix(".srt")
                    write_srt(result["segments"], str(srt_path), show_speaker=True)

                    for seg in result["segments"]:
                        line = f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}"
                        out_file.write(line + "\n")
                        full_transcript += line + "\n"
                    out_file.write("\n")
                    full_transcript += "\n"

                    self.update_progress(i / total_chunks * 100)
                    self.update_status(f"status:: Chunk {i}/{total_chunks} done")

            self.update_status("status:: Transcription complete!")

        except Exception as e:
            self.update_status(f"status:: Error: {e}")
        finally:
            if not self.keep_temp:
                self.cleanup()

        return full_transcript


    def extract_audio(self):
        command = [
            "ffmpeg", "-i", str(self.video),
            "-ar", "16000", "-ac", "1",
            "-c:a", "pcm_s16le", str(self.audio_file), "-y"
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    def split_audio(self, overlap_sec=3):
        self.chunk_dir.mkdir(exist_ok=True)
        audio = AudioSegment.from_wav(self.audio_file)
        total_length = len(audio)

        chunk_len_ms = self.chunk_length * 1000
        overlap_ms = overlap_sec * 1000
        step = chunk_len_ms - overlap_ms
        count = 0

        if total_length < chunk_len_ms:
            chunk_path = self.chunk_dir / "chunk_000.wav"
            audio.export(chunk_path, format="wav")
            return

        for start in range(0, total_length, step):
            end = min(start + chunk_len_ms, total_length)
            chunk = audio[start:end]
            chunk_path = self.chunk_dir / f"chunk_{count:03d}.wav"
            chunk.export(chunk_path, format="wav")
            count += 1

        self.update_status(f"Created {count} overlapping chunks.")

    def cleanup(self):
        if self.audio_file.exists():
            self.audio_file.unlink()
        if self.chunk_dir.exists():
            shutil.rmtree(self.chunk_dir)

    def prepare_audio(self):
        self.update_status("status:: Extracting audio...")
        self.extract_audio()

        self.update_status("status:: Splitting audio...")
        self.split_audio()

    def load_model_and_chunks(self):
        self.update_status("status:: Loading Whisper model...")
        model = whisper.load_model(self.model_name)

        chunks = sorted(self.chunk_dir.glob("chunk_*.wav"))
        total_chunks = len(chunks)
        self.update_status(f"status:: Transcribing {total_chunks} chunks...")

        return model, chunks, total_chunks
