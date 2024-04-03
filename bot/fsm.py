from aiogram.fsm.state import StatesGroup, State



### Client ###


class Payment(StatesGroup):
    payment = State()