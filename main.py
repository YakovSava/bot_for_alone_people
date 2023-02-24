import asyncio

from sys import platform
from multiprocessing import Process
from pyqiwip2p import AioQiwiP2P
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, \
	CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from plugins.database import Database
from plugins.dispatcher import Dispatcher as dis
from plugins.compliments import ComplimentsGetter
from plugins.states import RegistrationState, EditState, PaymentState
from plugins.storage import Storage
from config import token, qiwi_token

if platform is ['win32', 'cygwin', 'msys']: asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

main_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_loop)

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
qiwi = AioQiwiP2P(qiwi_token)

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
	if (await database.exists(message.from_id)):
		await EditState.cid.set()
		await message.answer('Вводи число снова, солнышко)')
	else:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add('/reg')
		await message.anwer('Ты не можешь поменять количество комплиментов в день, пока не зарегестрируешься. Зарегестрируйся пожалуйста, солнышко', reply_markup=keyboard)

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
	if (await database.exists(message.from_id)):
		await EditState.name.set()
		await message.answer('Вводи новое имя, прелесть')
	else:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add('/reg')
		await message.anwer('Ты не можешь менять имя пока не зарегестрирован, солнышко', reply_markup=keyboard)

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
	if (await database.exists(message.from_id)):
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add('/menu')
		await message.answer(await compget.get(), reply_markup=keyboard)
	else:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add('/reg')
		await message.anwer('Солнце, я не знаю за что выдавать тебе комплименты. Давай вот зарегестрируйся, а потом можешь просить комлпименты, сколько хочешь :3', reply_markup=keyboard)

@dp.message_handler(commands=['dev'])
async def print_dev_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add('/menu')
	await message.answer('Бот написан разработчиком https://t.me/dc11gh58', reply_markup=keyboard)

@dp.message_handler(commands=['donate'])
async def donate_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	if (await database.exists(message.from_id)):
		keyboard.add('/qiwi')
		await message.answer('Это донат. Он не обязателен, бот работает абсолютно бесплатно и не требует каких-нибудь подписок и т.п.\n\
Но к сожаленнию сервера что-то, но стоят, потому тут есть эта кнопочка и ниже варианты как можно задонатить', reply_markup=keyboard)
	else:
		keyboard.add('/reg')
		await message.anwer('Солнышко, я понимаю что ты хочешь помочь нам, но героев надо знать в лицо. Зарегестрируйся пожалуйста', reply_markup=keyboard)

@dp.message_handler(commands=['qiwi'])
async def qiwi_handler(message:Message):
	if (await database.exists(message.from_id)):
		await message.answer('Напиши сколько ты хочешь задонатить!')
		await PaymentState.qiwi.set()
	else:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add('/reg')
		await message.anwer('Солнышко, я понимаю что ты хочешь помочь нам, но героев надо знать в лицо. Зарегестрируйся пожалуйста', reply_markup=keyboard)

@dp.message_handler(state=PaymentState.qiwi)
async def qiwi_pay_handler(message:Message, state:FSMContext):
	if message.text.isdigit():
		amount = int(message.text)
	else:
		amount = 50
	await state.finish()
	price = await qiwi.bill(amount=amount)
	back = ReplyKeyboardMarkup(resize_keyboard=True)
	back.add('/menu')
	check = InlineKeyboardMarkup()
	check.add(InlineKeyboardButton(text='Проверка оплаты', callback_data='checker'))
	await message.answer(f'Вот твоя индивидуальная ссылка на оплату {amount} руб.: {price.pay_url}', reply_markup=check)
	await message.answer('Ссылка живёт 15 минут, поторопись оплатить!\n\
после оплаты нажми на кнопку, пожалуйста...', reply_markup=back)
	storage.set(f'{message.from_id}_checker', price.bill_id)

@dp.callback_query_handler(text='checker')
async def check_pay(call:CallbackQuery):
	bill_price = await qiwi.bill(bill_id=storage.get(f'{call.message.from_id}_checker'))
	if bill_price.status == 'PAID':
		await call.message.edit_text('Вы успешно оплатили бота!')
	else:
		await call.answer(text='Ещё не оплачено!', show_alert=True)

def polling():
	executor.start_polling(dp, skip_updates=True, loop=asyncio.get_event_loop())

if __name__ == '__main__':
	p = Process(target=polling)
	p.start()
	main_loop.run_until_complete(dispatcher.checker())