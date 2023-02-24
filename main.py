import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.typing import Message, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import token
from plugins.database import Database
from plugins.dispatcher import Dispatcher as dis
from plugins.compliments import ComplimentsGetter
from plugins.states import RegistrationState, EditState, PaymentState
from plugins.storage import Storage

main_loop = asyncio.get_event_loop()

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())
compget = ComplimentsGetter(loop=main_loop)
database = Database(loop=main_loop)
dispatcher = dis(
	loop=main_loop,
	database=database,
	compliments=compget,
	bot=bot
)
storage = Storage()

@dp.message_handler(commands=['start'])
async def start_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	if (await database.exists(message.from_id)):
		keyboard.add(*['/reg'])
		await message.answer('Привет, солнышко!\nКак твои дела? Прости пожалуйста, но что бы пользоваться мной тебе надо будет зарегестрироваться!', reply_markup=keyboard)
	else:
		keyboard.add(*['/menu'])
		await message.answer('Привет, прелесть!\nКак твои дела? Давай в меню :3', reply_markup=keyboard)

@dp.message_handler(commands=['menu'])
async def menu_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	if (await database.exists(message.from_id)):
		keyboard.add(*[
			'/compliment',
			'/change'
		])
		keyboard.add(*[
			'/dev',
			'/donate'
		])
		await message.answer('Ой, моя прелесть вернулась. Выбирай действие, солнце)', reply_markup=keyboard)
	else:
		keyboard.add('/reg')
		await message.answer('Ну блин, милашка, я же просил(а) что надо зарегестрироваться. Вот кнопочка :3', reply_markup=keyboard)

@dp.message_handler(commands=['change'])
async def change_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	if (await database.exists(message.from_id)):
		keyboard.add(*[
			'/cid',
			'/name'
		])
		keyboard.add('/menu')
		await message.answer('Вот кнопочки, "/cid" - compliments in day, комплименты в день. Их может быть от 1 до 12, каждый часик.\n\
А вот "/name" это смена имени')
	else:
		keyboard.add('/reg')
		await message.answer('Ну блин, милашка, я же просил(а) что надо зарегестрироваться. Вот кнопочка :3', reply_markup=keyboard)

@dp.message_handler(commands=['reg'])
async def registration_handler(message:Message):
	if (await database.exists(message.from_id)):
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add('/menu')
		await message.answer('Солнышко, ты уже зарегестрирован. Тебе не надо больше зарегестрироваться, прелесть :3', reply_markup=keyboard)
	else:
		await message.answer('Вот ты зарегестрируешься, милый, тебе стоит сначал ввести... Имя! Давай, вводи скорее, прелесть)')
		await RegistrationState.name.set()

@dp.message_handler(state=RegistrationState.name)
async def reg_name_step(message:Message, state:FSMContext):
	await RegistrationState.cid.set()
	await message.answer(f'Вау, {message.text} - прекрасное имя. Давай теперь введи сколько комплиментов в день ты хочешь получать.\n\
Солнышко. только вводи пожалуйста число от 1 до 12, прошу!')
	storage.set(index_name=f'{message.from_id}_name', element=message.text)

@dp.message_handler(state=RegistrationState.cid)
async def reg_cid_step(message:Message, state:FSMContext):
	if message.text.isdigit():
		if 12 >= int(message.text) >= 1:
			await state.finish()
			name = storage.get(index=f'{message.from_id}_name'); storage.delete(index=f'{message.from_id}_name')
			await database.reg(data={
				'id': message.from_id,
				'name': name,
				'cid': int(message.text)
			})
			keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
			keyboard.add('/menu')
			await message.answer('Теперь ты, прелесть, зарегестрирован. Нажимай на кнопочку и смотри на новые функции :3', reply_markup=keyboard)
		else:
			if int(message.text) == 42:
				await message.answer('Тут нельзя получить жизнь!')
			else:
				await message.answer('Солнце, введи число в промежутке от 1 до 12 включительно')
	else:
		await message.answer('Солнце, введи пожалуйста число, прошу')

@dp.message_handler(commands=['cid'])
async def edit_cid_handler(message:Message):
	await EditState.cid.set()
	await message.answer('Вводи число снова, солнышко)')

@dp.message_handler(state=EditState.cid)
async def edit_cid_step2_handler(message:Message, state:FSMContext):
	if message.text.isdigit():
		if 12 >= int(message.text) >= 1:
			await state.finish()
			keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
			keyboard.add('/menu')
			await message.answer(f'Вот теперь ты будешь получать {message.text} комплиментов в день, солнце)', reply_markup=keyboard)
			await database.edit_cid(
				edit_id=message.from_id,
				cid=int(message.text)
			)
		else:
			if int(message.text) == 42:
				await message.answer('Тут нельзя получить жизнь!')
			else:
				await message.answer('Солнце, введи число в промежутке от 1 до 12 включительно')
	else:
		await message.answer('Солнце, введи пожалуйста число, прошу')

@dp.message_handler(commands=['name'])
async def edit_name_handler(message:Message):
	await EditState.name.set()
	await message.answer('Вводи новое имя, прелесть')

@dp.message_handler(state=EditState.name)
async def edit_name_step2_handler(message:Message, state:FSMContext):
	await state.finish()
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add('/menu')
	await message.answer(f'Вот, теперь ты назван(а) прекрасным именем - {message.text}', reply_markup=keyboard)
	await database.edit_name(
		edit_id=message.from_id,
		new_name=message.text
	)

@dp.message_handler(commands=['compliment', 'comp'])
async def compliments_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add('/menu')
	await message.answer(await compget.get(), reply_markup=keyboard)

@dp.message_handler(commands=['dev'])
async def print_dev_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add('/menu')
	await message.answer('Бот написан разработчиком https://t.me/dc11gh58', reply_markup=keyboard)

# @dp.message_handler(commands=['donate'])
# async def 

async def polling():
	executor.start_polling(dp, skip_updates=True, loop=main_loop)

if __name__ == '__main__':
	main_loop.run_until_complete(
		asyncio.wait(
			main_loop.create_task(dispatcher.checker()),
			main_loop.create_task(polling())
		)
	)