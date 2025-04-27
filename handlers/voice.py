from aiogram import Router, F, types
from aiogram.enums import ChatAction
from services.stt import transcribe_audio
from services.rag import query_model
from services.tts import generate_speech
import tempfile
import os
# --- Import necessary functions ---
from database.db import get_profiles_by_telegram_id  # Import DB function
from utils.keyboards import get_start_keyboard  # Import keyboard for the prompt

router = Router()

def register_voice_handlers(dp):
    dp.include_router(router)

@router.message(F.voice)
async def handle_voice(message: types.Message):
    telegram_id = message.from_user.id

    # --- Authentication Check ---
    profiles = await get_profiles_by_telegram_id(telegram_id)
    if not profiles:
        await message.answer(
            "⚠️ Bu funksiyadan foydalanish uchun avval ro'yxatdan o'ting yoki tizimga kiring.",
            reply_markup=get_start_keyboard() # Provide registration/login options
        )
        return # Stop processing if user not found
    # --- End Authentication Check ---

    # If the check passes, proceed with voice processing
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    voice = message.voice
    file_info = await message.bot.get_file(voice.file_id)
    # file_path = file_info.file_path # Not directly used, path derived below

    with tempfile.TemporaryDirectory() as tmpdir:
        # Use file_info.file_path to get suggested filename if needed, but unique_id is safer
        input_path = os.path.join(tmpdir, f"{voice.file_unique_id}.ogg")
        output_path = os.path.join(tmpdir, f"{voice.file_unique_id}.wav")
        tts_output = os.path.join(tmpdir, f"answer_{voice.file_unique_id}.mp3") # Make TTS output unique too

        # Correctly use file_info.file_id with bot.download
        await message.bot.download_file(file_path=file_info.file_path, destination=input_path)

        text = await transcribe_audio(input_path, output_path)
        if not text:
            await message.answer("❌ Ovozdan matn ajratib bo‘lmadi. Aniqroq gapirishga harakat qiling.")
            return # Stop if transcription fails

        await message.reply(f"📄 Matn: <i>{text}</i>", parse_mode="HTML")

        # Add thinking indicator before querying model
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING
        )

        answer = await query_model(text)
        if not answer or answer == "Javob topilmadi.": # Check for specific no-answer message
            await message.answer("🤔 Savolingizga hozircha javob topa olmadim.")
            return # Stop if no answer found

        # Add voice generation indicator
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.RECORD_VOICE # Or UPLOAD_VOICE
        )

        success = await generate_speech(answer, tts_output)
        if success:
            try:
                await message.answer_voice(types.FSInputFile(tts_output))
            except Exception as e:
                # Fallback if sending voice fails for some reason
                print(f"Error sending voice: {e}") # Log the error
                await message.answer(f"📝 Javob (ovozli yuborishda xatolik):\n\n{answer}")
        else:
            await message.answer(f"📝 Javob (ovoz sintezida xatolik):\n\n{answer}")