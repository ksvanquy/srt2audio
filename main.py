import argparse
import sys
from pathlib import Path
from srt_parser import extract_full_text
from tts_engine import generate_audio
from aligner import transcribe_audio, write_chunked_srt, write_word_level_srt

def get_word_srt_path(sync_srt_path: str, word_srt_path: str) -> str:
    if word_srt_path:
        return word_srt_path
    sync_path = Path(sync_srt_path)
    return str(sync_path.with_name(f"{sync_path.stem}_word_by_word{sync_path.suffix}"))

def validate_output_paths(output_path: str, sync_srt_path: str, word_srt_path: str):
    paths = {
        "audio output": Path(output_path).resolve(),
        "synced SRT output": Path(sync_srt_path).resolve(),
        "word-by-word SRT output": Path(word_srt_path).resolve(),
    }
    unique_paths = set(paths.values())
    if len(unique_paths) != len(paths):
        duplicates = ", ".join(
            name for name, path in paths.items() if list(paths.values()).count(path) > 1
        )
        raise ValueError(f"Các file output bị trùng đường dẫn: {duplicates}.")

def main():
    parser = argparse.ArgumentParser(
        description="Chuyển đổi SRT sang Audio và tự động Smart Chunking phụ đề chuẩn CapCut kèm Word-by-Word."
    )
    parser.add_argument("input", nargs="?", default="input.srt", help="Đường dẫn file SRT đầu vào (mặc định: input.srt).")
    parser.add_argument("-o", "--output", default="output.mp3", help="File audio đầu ra.")
    parser.add_argument("-s", "--sync-srt", default="synced_output.srt", help="File SRT đồng bộ mới (Smart Chunking).")
    parser.add_argument("-w", "--word-srt", default="", help="Tên file SRT dạng word-by-word đầu ra (để trống sẽ tự động đặt tên theo synced-srt).")
    parser.add_argument("-v", "--voice", default="vi-VN-HoaiMyNeural", help="Giọng đọc Edge TTS.")
    parser.add_argument("-r", "--rate", default="+0%", help="Tốc độ đọc.")
    parser.add_argument("--volume", default="+0%", help="Âm lượng.")
    parser.add_argument("--pitch", default="+0Hz", help="Độ cao giọng đọc.")
    parser.add_argument("--whisper-model", default="medium", help="Model Whisper (khuyên dùng medium hoặc small).")
    parser.add_argument("--prompt", default="", help="Đoạn văn bản mẫu định hướng từ vựng cho Whisper.")
    parser.add_argument("--max-chars", type=int, default=40, help="Số ký tự tối đa cho mỗi đoạn phụ đề (mặc định: 40).")

    args = parser.parse_args()
    word_srt_path = get_word_srt_path(args.sync_srt, args.word_srt)
    try:
        validate_output_paths(args.output, args.sync_srt, word_srt_path)
    except ValueError as e:
        parser.error(str(e))

    print(f"\n--- [BƯỚC 1]: TRÍCH XUẤT VĂN BẢN ---")
    try:
        full_text = extract_full_text(args.input)
        initial_prompt = args.prompt if args.prompt else full_text[:200]
        print(f"[Thành công] Đã lấy toàn bộ văn bản từ {args.input}.")
    except Exception as e:
        print(f"[Lỗi] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- [BƯỚC 2]: TẠO AUDIO LIÊN TỤC (EDGE-TTS) ---")
    try:
        generate_audio(
            text=full_text, voice=args.voice, output_file=args.output,
            rate=args.rate, volume=args.volume, pitch=args.pitch
        )
        print(f"[Thành công] Đã lưu file audio tại: {args.output}")
    except Exception as e:
        print(f"[Lỗi TTS] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- [BƯỚC 3]: SMART CHUNKING & ALIGNMENT ---")
    try:
        transcription = transcribe_audio(
            audio_path=args.output,
            model_size=args.whisper_model,
            initial_prompt=initial_prompt,
        )
        write_chunked_srt(transcription, args.sync_srt, args.max_chars)
        print(f"\n[HOÀN TẤT] Subtitle Smart Chunking đã được tạo thành công!")
    except Exception as e:
        print(f"[Lỗi Alignment] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- [BƯỚC 4]: XUẤT PHỤ ĐỀ WORD-BY-WORD ---")
    try:
        write_word_level_srt(transcription, word_srt_path)
        print(f"\n[HOÀN TẤT] Subtitle Word-by-Word đã được tạo thành công tại: {word_srt_path}")
    except Exception as e:
        print(f"[Lỗi Word-by-Word] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()