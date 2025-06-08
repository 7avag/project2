# routers/commands.py

import json
import asyncio
import random
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from config.settings import settings
from services.api_client import APIClient
from keyboards.builders import main_menu
from keyboards.inline import note_actions_keyboard
from filters.admin_filter import IsAdminFilter
from states.notes_state import NotesStates

router = Router()
api_client = APIClient()

# Список русских шуток
RUSSIAN_JOKES = [
    "Как-то раз программист зашел в бар, бармен спросил: «Что будете?» Программист ответил: «Да похоже, что забыли точку с запятой... Почему всё падает?»",
    "— Алло, это техподдержка? У меня ничего не работает! — А вы пробовали выключить и включить? — Да. — Отлично, опишите проблему снова.",
    "— Почему программисты путают Halloween и Christmas? — Потому что OCT 31 == DEC 25.",
    "Если баг находится на вашем компьютере — это ошибка. Если вы нашли баг у коллеги — это фича."
]

def load_locale(lang: str) -> dict:
    with open(f"locales/{lang}.json", encoding="utf-8") as f:
        return json.load(f)

def load_user_notes(user_id: str) -> list[dict]:
    try:
        with open(settings.STORAGE_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        return db["users"].get(user_id, [])
    except Exception:
        return []

def format_notes_list(notes: list[dict], lang: str) -> str:
    if not notes:
        return load_locale(lang)["notes_list_empty"]
    lines = []
    for n in notes:
        date, time_part = n["timestamp"].split("T")
        time_part = time_part[:8]
        lines.append(f"ID {n['id']}: {n['text']} ({date} {time_part})")
    return "\n".join(lines)

# Кнопки
BUTTON_HELP_RU = "ℹ️ Помощь"
BUTTON_HELP_EN = "ℹ️ Help"
BUTTON_JOKE_RU = "🤣 Шутка"
BUTTON_JOKE_EN = "🤣 Joke"
BUTTON_LANGUAGE_RU = "🌐 Язык"
BUTTON_LANGUAGE_EN = "🌐 Language"
BUTTON_NOTES_RU = "📃 Мои заметки"
BUTTON_NOTES_EN = "📃 My Notes"

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # При первом запуске выставляем русский по умолчанию
    await state.update_data(lang="ru")
    locale = load_locale("ru")
    text = locale["start_text"].format(user_name=message.from_user.full_name)
    keyboard = main_menu("ru")
    await message.answer(text, reply_markup=keyboard)

@router.message(Command("help"))
@router.message(lambda m: m.text == BUTTON_HELP_RU or m.text == BUTTON_HELP_EN)
async def cmd_help(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)
    await message.answer(locale["help_text"])

@router.message(Command("joke"))
@router.message(lambda m: m.text == BUTTON_JOKE_RU or m.text == BUTTON_JOKE_EN)
async def cmd_joke(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")

    if message.text == BUTTON_JOKE_EN or lang == "en":
        locale = load_locale("en")
        await message.answer(locale["joke_loading"])
        joke = await api_client.get_random_joke()
        await message.answer(f"🤣 {joke}")
    else:
        joke = random.choice(RUSSIAN_JOKES)
        await message.answer(f"🤣 {joke}")

@router.message(Command("language"))
@router.message(lambda m: m.text == BUTTON_LANGUAGE_RU or m.text == BUTTON_LANGUAGE_EN)
async def cmd_language(message: Message, state: FSMContext):
    data = await state.get_data()
    current = data.get("lang", "ru")
    new_lang = "en" if current == "ru" else "ru"
    await state.update_data(lang=new_lang)
    locale = load_locale(new_lang)
    keyboard = main_menu(new_lang)
    await message.answer(locale["language_changed"].format(lang=new_lang), reply_markup=keyboard)

@router.message(Command("notes"))
@router.message(lambda m: m.text == BUTTON_NOTES_RU or m.text == BUTTON_NOTES_EN)
async def cmd_notes(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)

    user_id = str(message.from_user.id)
    notes = load_user_notes(user_id)
    notes_list = format_notes_list(notes, lang)

    await message.answer(notes_list)
    await message.answer(locale["notes_menu"], reply_markup=note_actions_keyboard(lang))

@router.callback_query(lambda c: c.data == "add_note")
async def cb_add_note(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)
    await callback.message.answer(locale["enter_note_text"])
    await state.set_state(NotesStates.WAITING_FOR_NOTE_TEXT)
    await callback.answer()

@router.callback_query(lambda c: c.data == "delete_note")
async def cb_delete_note(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)
    await callback.message.answer(locale["enter_delete_id"])
    await state.set_state(NotesStates.WAITING_FOR_DELETE_ID)
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)
    await callback.message.answer(locale["action_canceled"])
    # Сбрасываем только состояние, оставляя данные (lang не меняется)
    await state.set_state(None)
    await callback.answer()

@router.message(NotesStates.WAITING_FOR_NOTE_TEXT)
async def process_note_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)

    text = message.text.strip()
    user_id = str(message.from_user.id)
    from datetime import datetime

    path = settings.STORAGE_PATH
    with open(path, "r+", encoding="utf-8") as f:
        db = json.load(f)
        user_notes = db["users"].get(user_id, [])
        new_id = 1 if not user_notes else max(n["id"] for n in user_notes) + 1
        note = {"id": new_id, "text": text, "timestamp": datetime.utcnow().isoformat()}
        user_notes.append(note)
        db["users"][user_id] = user_notes
        f.seek(0)
        json.dump(db, f, ensure_ascii=False, indent=4)
        f.truncate()

    await message.answer(locale["note_added"].format(note_id=new_id))
    # Сбрасываем только состояние, оставляя данные (lang не меняется)
    await state.set_state(None)

@router.message(NotesStates.WAITING_FOR_DELETE_ID)
async def process_delete_id(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)

    try:
        note_id = int(message.text.strip())
    except ValueError:
        await message.answer(locale["invalid_id"])
        return

    user_id = str(message.from_user.id)
    path = settings.STORAGE_PATH
    with open(path, "r+", encoding="utf-8") as f:
        db = json.load(f)
        user_notes = db["users"].get(user_id, [])
        filtered = [n for n in user_notes if n["id"] != note_id]
        if len(filtered) == len(user_notes):
            await message.answer(locale["note_not_found"].format(note_id=note_id))
            return
        db["users"][user_id] = filtered
        f.seek(0)
        json.dump(db, f, ensure_ascii=False, indent=4)
        f.truncate()

    await message.answer(locale["note_deleted"].format(note_id=note_id))
    # Сбрасываем только состояние, оставляя данные (lang не меняется)
    await state.set_state(None)

@router.message(Command("broadcast"), IsAdminFilter())
async def cmd_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)

    parts = message.text.split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply(locale["broadcast_usage"])
        return
    text = parts[1].strip()

    path = settings.STORAGE_PATH
    with open(path, "r", encoding="utf-8") as f:
        db = json.load(f)
    users = db["users"].keys()

    sent = 0
    failed = 0
    for uid in users:
        try:
            await message.bot.send_message(int(uid), f"{locale['broadcast_prefix']} {text}")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await message.reply(locale["broadcast_result"].format(sent=sent, failed=failed))

@router.message(Command("stats"), IsAdminFilter())
async def cmd_stats(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    locale = load_locale(lang)

    path = settings.STORAGE_PATH
    with open(path, "r", encoding="utf-8") as f:
        db = json.load(f)
    total_users = len(db["users"])
    await message.answer(locale["stats_text"].format(count=total_users))

@router.message(lambda m: m.text == BUTTON_NOTES_RU or m.text == BUTTON_NOTES_EN)
async def text_notes_menu(message: Message, state: FSMContext):
    await cmd_notes(message, state)

@router.message(lambda m: m.text == BUTTON_HELP_RU or m.text == BUTTON_HELP_EN)
async def text_help_menu(message: Message, state: FSMContext):
    await cmd_help(message, state)
