from faster_whisper import WhisperModel

def format_srt_time(seconds: float) -> str:
    """Chuyển đổi giây thành định dạng chuẩn SRT (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def align_audio_to_srt(audio_path: str, output_srt_path: str, model_size: str = "medium", initial_prompt: str = None, max_chars_per_line: int = 40):
    """
    Thực hiện Forced Alignment kèm thuật toán Smart Chunking (chuẩn CapCut) 
    dựa trên mốc thời gian từng từ (Word-level Timestamps).
    """
    print(f"[*] Đang tải mô hình Whisper ({model_size}) để phân tích từ chi tiết...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print("[*] Đang bóc tách mốc thời gian từng từ và gom nhóm văn bản...")
    segments, _ = model.transcribe(
        audio_path, 
        beam_size=5, 
        language="vi", 
        initial_prompt=initial_prompt,
        word_timestamps=True
    )
    
    subtitles = []
    
    for segment in segments:
        if not segment.words:
            # Fallback nếu segment không có word-level timestamps chi tiết
            subtitles.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
            continue
            
        current_chunk_words = []
        current_chars_count = 0
        chunk_start_time = segment.words[0].start
        
        for word_obj in segment.words:
            word_text = word_obj.word.strip()
            word_len = len(word_text) + 1 # Tính cả khoảng trắng
            
            # Nếu vượt quá giới hạn ký tự cho phép, đóng gói chunk hiện tại lại
            if current_chars_count + word_len > max_chars_per_line and current_chunk_words:
                chunk_end_time = current_chunk_words[-1].end
                subtitles.append({
                    "start": chunk_start_time,
                    "end": chunk_end_time,
                    "text": " ".join([w.word.strip() for w in current_chunk_words])
                })
                current_chunk_words = [word_obj]
                current_chars_count = word_len
                chunk_start_time = word_obj.start
            else:
                current_chunk_words.append(word_obj)
                current_chars_count += word_len
                
        # Thêm phần còn lại của segment
        if current_chunk_words:
            chunk_end_time = current_chunk_words[-1].end
            subtitles.append({
                "start": chunk_start_time,
                "end": chunk_end_time,
                "text": " ".join([w.word.strip() for w in current_chunk_words])
            })

    # Ghi ra file SRT chuẩn
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for i, sub in enumerate(subtitles, start=1):
            start_str = format_srt_time(sub["start"])
            end_str = format_srt_time(sub["end"])
            
            f.write(f"{i}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{sub['text']}\n\n")
            
    print(f"[Thành công] Đã tạo file Smart SRT (tối đa {max_chars_per_line} ký tự/dòng) tại: {output_srt_path}")

def export_word_level_srt(audio_path: str, output_srt_path: str, model_size: str = "medium", initial_prompt: str = None):
    """
    Trích xuất phụ đề chi tiết dạng word-by-word (mỗi dòng SRT là 1 từ đơn lẻ) 
    dựa trên word-level timestamps gốc từ faster_whisper.
    """
    print(f"[*] Đang tải mô hình Whisper ({model_size}) để bóc tách từng từ...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    segments, _ = model.transcribe(
        audio_path, 
        beam_size=5, 
        language="vi", 
        initial_prompt=initial_prompt,
        word_timestamps=True
    )
    
    word_entries = []
    counter = 1
    
    for segment in segments:
        if not segment.words:
            continue
        for word_obj in segment.words:
            word_text = word_obj.word.strip()
            if not word_text:
                continue
            word_entries.append({
                "index": counter,
                "start": word_obj.start,
                "end": word_obj.end,
                "text": word_text
            })
            counter += 1

    # Ghi ra file SRT định dạng Word-by-Word
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for item in word_entries:
            start_str = format_srt_time(item["start"])
            end_str = format_srt_time(item["end"])
            
            f.write(f"{item['index']}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{item['text']}\n\n")
            
    print(f"[Thành công] Đã xuất file Subtitle Word-by-Word tại: {output_srt_path}")