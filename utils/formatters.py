# utils/formatters.py

from datetime import datetime

def format_note(note: dict) -> str:
    """
    Форматирует словарь заметки в строку для вывода пользователю.
    Ожидается, что note = {"id": int, "text": str, "timestamp": str}
    """
    ts = datetime.fromisoformat(note["timestamp"])
    note_text = note["text"]
    return f"📝 ID: {note['id']}\n{note_text}\n⏲️ Дата: {ts.strftime('%Y-%m-%d %H:%M:%S')}"
