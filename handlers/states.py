from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):

    choosing_language = State()
    waiting_subscription = State()
    ready = State()
    admin_waiting_reset_user_id = State()
