from aiogram.dispatcher.filters.state import State, StatesGroup

class RegistrationState(StatesGroup):
	name = State()
	cid = State()

class EditState(StatesGroup):
	name = State()
	cid = State()

class PaymentState(StatesGroup):
	qiwi = State()