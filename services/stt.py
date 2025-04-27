from transformers import pipeline
import pydub

model = pipeline("automatic-speech-recognition", model="jamshidahmadov/whisper-uz")

async def transcribe_audio(ogg_path: str, wav_path: str) -> str | None:
    pydub.AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")
    result = model(wav_path)
    return result["text"] if result and "text" in result else None
