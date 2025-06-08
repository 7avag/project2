from aiogram.fsm.state import StatesGroup, State

class NotesStates(StatesGroup):
    WAITING_FOR_NOTE_TEXT = State()
    WAITING_FOR_DELETE_ID = State()
