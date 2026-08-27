import asyncio
import edge_tts

async def _generate_continuous_audio(text: str, voice: str, output_file: str, rate: str, volume: str, pitch: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
    await communicate.save(output_file)

def generate_audio(text: str, voice: str, output_file: str, rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz"):
    """Gọi Edge-TTS để tạo một file audio đọc một mạch tự nhiên, không bị ngắt quãng cứng nhắc."""
    asyncio.run(_generate_continuous_audio(text, voice, output_file, rate, volume, pitch))