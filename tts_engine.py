import asyncio
import os
import re
import tempfile
from pathlib import Path
import edge_tts

MAX_TTS_CHARS = 3000

def _split_text(text: str, max_chars: int = MAX_TTS_CHARS):
    sentences = re.split(r"(?<=[.!?。！？])\s+", text.strip())
    chunks = []
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        if len(sentence) > max_chars:
            words = sentence.split()
            for word in words:
                if current and len(current) + len(word) + 1 > max_chars:
                    chunks.append(current)
                    current = ""
                current = f"{current} {word}".strip()
            continue
        if current and len(current) + len(sentence) + 1 > max_chars:
            chunks.append(current)
            current = ""
        current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks

async def _generate_continuous_audio(text: str, voice: str, output_file: str, rate: str, volume: str, pitch: str):
    output_path = Path(output_file)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=output_path.parent or Path("."),
            prefix=f".{output_path.name}.", suffix=".tmp", delete=False
        ) as output:
            temporary_path = Path(output.name)
            for chunk in _split_text(text):
                communicate = edge_tts.Communicate(chunk, voice, rate=rate, volume=volume, pitch=pitch)
                async for message in communicate.stream():
                    if message["type"] == "audio":
                        output.write(message["data"])
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

def generate_audio(text: str, voice: str, output_file: str, rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz"):
    """Gọi Edge-TTS để tạo một file audio đọc một mạch tự nhiên, không bị ngắt quãng cứng nhắc."""
    asyncio.run(_generate_continuous_audio(text, voice, output_file, rate, volume, pitch))