import edge_tts

async def generate_speech(text: str, path: str) -> bool:
    try:
        tts = edge_tts.Communicate(text, "uz-UZ-SardorNeural")
        await tts.save(path)
        return True
    except Exception:
        return False
