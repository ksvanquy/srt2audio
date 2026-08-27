import math
import os
import tempfile
from pathlib import Path
from faster_whisper import WhisperModel

def format_srt_time(seconds: float) -> str:
    """Chuyển đổi giây thành định dạng chuẩn SRT (HH:MM:SS,mmm)."""
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Timestamp phải là số hữu hạn không âm.")

    total_milliseconds = int(seconds * 1000 + 0.5)
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def transcribe_audio(audio_path: str, model_size: str = "medium", initial_prompt: str = None):
    """Nhận dạng audio một lần và materialize toàn bộ word-level timestamps."""
    print(f"[*] Đang tải mô hình Whisper ({model_size}) để phân tích từ chi tiết...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("[*] Đang bóc tách mốc thời gian từng từ...")
    segments, _ = model.transcribe(
        audio_path,
        beam_size=5,
        language="vi",
        initial_prompt=initial_prompt,
        word_timestamps=True,
    )

    transcription = []
    for segment in segments:
        words = []
        if segment.words:
            words = [
                {"start": word.start, "end": word.end, "text": word.word.strip()}
                for word in segment.words
                if word.word.strip()
            ]
        transcription.append(
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": words,
            }
        )
    return transcription

def _write_srt_atomic(output_srt_path: str, subtitles):
    output_path = Path(output_srt_path)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output_path.parent or Path("."),
            prefix=f".{output_path.name}.", suffix=".tmp", delete=False
        ) as file:
            temporary_path = Path(file.name)
            for index, subtitle in enumerate(subtitles, start=1):
                file.write(f"{index}\n")
                file.write(
                    f"{format_srt_time(subtitle['start'])} --> "
                    f"{format_srt_time(subtitle['end'])}\n"
                )
                file.write(f"{subtitle['text']}\n\n")
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

def build_chunked_subtitles(transcription, max_chars_per_line: int = 40):
    subtitles = []
    for segment in transcription:
        words = segment["words"]
        if not words:
            if segment["text"]:
                subtitles.append({"start": segment["start"], "end": segment["end"], "text": segment["text"]})
            continue

        current_chunk_words = []
        current_chars_count = 0
        chunk_start_time = words[0]["start"]
        for word in words:
            word_len = len(word["text"]) + 1
            if current_chunk_words and current_chars_count + word_len > max_chars_per_line:
                subtitles.append({
                    "start": chunk_start_time,
                    "end": current_chunk_words[-1]["end"],
                    "text": " ".join(item["text"] for item in current_chunk_words),
                })
                current_chunk_words = []
                current_chars_count = 0
                chunk_start_time = word["start"]
            current_chunk_words.append(word)
            current_chars_count += word_len

        if current_chunk_words:
            subtitles.append({
                "start": chunk_start_time,
                "end": current_chunk_words[-1]["end"],
                "text": " ".join(item["text"] for item in current_chunk_words),
            })
    return subtitles

def build_word_subtitles(transcription):
    return [
        {"start": word["start"], "end": word["end"], "text": word["text"]}
        for segment in transcription
        for word in segment["words"]
    ]

def write_chunked_srt(transcription, output_srt_path: str, max_chars_per_line: int = 40):
    subtitles = build_chunked_subtitles(transcription, max_chars_per_line)
    _write_srt_atomic(output_srt_path, subtitles)
    print(f"[Thành công] Đã tạo file Smart SRT (tối đa {max_chars_per_line} ký tự/dòng) tại {output_srt_path}")

def write_word_level_srt(transcription, output_srt_path: str):
    _write_srt_atomic(output_srt_path, build_word_subtitles(transcription))
    print(f"[Thành công] Đã xuất file Subtitle Word-by-Word tại {output_srt_path}")

def align_audio_to_srt(audio_path: str, output_srt_path: str, model_size: str = "medium", initial_prompt: str = None, max_chars_per_line: int = 40):
    transcription = transcribe_audio(audio_path, model_size, initial_prompt)
    write_chunked_srt(transcription, output_srt_path, max_chars_per_line)

def export_word_level_srt(audio_path: str, output_srt_path: str, model_size: str = "medium", initial_prompt: str = None):
    transcription = transcribe_audio(audio_path, model_size, initial_prompt)
    write_word_level_srt(transcription, output_srt_path)