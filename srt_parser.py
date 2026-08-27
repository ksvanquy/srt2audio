import pysrt
import re

def extract_full_text(srt_path: str) -> str:
    """Đọc file SRT và gom toàn bộ văn bản lại thành một chuỗi liên tục."""
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')
    except Exception as e:
        raise ValueError(f"Không thể đọc file SRT: {e}")
    
    text_lines = []
    for sub in subs:
        clean_text = re.sub(r'<.*?>', '', sub.text)
        clean_text = clean_text.replace('\n', ' ').strip()
        if clean_text:
            text_lines.append(clean_text)
            
    return " ".join(text_lines)