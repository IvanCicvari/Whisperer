def format_timestamp(seconds: float) -> str:
    """Format time in seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    millis = round((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def write_srt(segments, file_path, show_speaker=False):
   
    with open(file_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()

            speaker = seg.get("speaker") or seg.get("speaker_label")
            if show_speaker and speaker:
                text = f"{speaker}: {text}"

            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
