# keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def note_actions_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """
    Inline-клавиатура для управления заметками: добавить, удалить, отмена.
    """
    if language == "ru":
        add_btn = InlineKeyboardButton(text="Добавить заметку", callback_data="add_note")
        delete_btn = InlineKeyboardButton(text="Удалить заметку", callback_data="delete_note")
        cancel_btn = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    else:
        add_btn = InlineKeyboardButton(text="Add note", callback_data="add_note")
        delete_btn = InlineKeyboardButton(text="Delete note", callback_data="delete_note")
        cancel_btn = InlineKeyboardButton(text="Cancel", callback_data="cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [add_btn, delete_btn],
            [cancel_btn]
        ]
    )
    return keyboard
