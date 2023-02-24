import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.typing import Message, ReplyKeyboardMarkup
from config import token
from plugins.database import Database
from plugins.dispatcher import Dispatcher as dis
from plugins.compliments import ComplimentsGetter

main_loop = asyncio.get_event_loop()

bot = Bot(token)
dp = Dispatcher(bot)
compget = ComplimentsGetter(loop=main_loop)
database = Database(loop=main_loop)
dispatcher = dis(
	loop=main_loop,
	database=database,
	compliments=compget,
	bot=bot
)

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

@dp.message_handler(commands=['/reg'])
async def registration_handler(message:Message):
	if (await database.exists(message.from_id)):
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		await message.answer('Солнышко, ты уже зарегестрирован. Тебе не надо больше зарегестрироваться, прелесть :3', reply_markup=keyboard)
	else:
		await message.answer('Вот ты зарегестрируешься, милый, тебе стоит сначал ввести... Имя! Давай, вводи скорее, прелесть)')

async def polling():
	executor.start_polling(dp, skip_updates=True, loop=main_loop)

if __name__ == '__main__':
	main_loop.run_until_complete(
		asyncio.wait(
			main_loop.create_task(dispatcher.checker()),
			main_loop.create_task(polling())
		)
	)