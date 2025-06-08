# keyboards/builders.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu(language: str = "ru") -> ReplyKeyboardMarkup:
    """
    Строит главное меню (reply-клавиатуру).
    """
    if language == "ru":
        buttons = ["📃 Мои заметки", "🤣 Шутка", "🌐 Язык", "ℹ️ Помощь"]
    else:
        buttons = ["📃 My Notes", "🤣 Joke", "🌐 Language", "ℹ️ Help"]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=buttons[0])],
            [KeyboardButton(text=buttons[1]), KeyboardButton(text=buttons[2])],
            [KeyboardButton(text=buttons[3])]
        ],
        resize_keyboard=True
    )
    return keyboard
