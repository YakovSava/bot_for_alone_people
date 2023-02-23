import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.typing import Message, ReplyKeyboardMarkup
from config import token

bot = Bot(token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_handler(message:Message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add(*['/reg']) if True else keyboard.add(*['/menu'])
	await message.answer('Привет, солнышко!\nКак твои дела? Прости пожалуйста, но что бы пользоваться мной тебе надо будет зарегестрироваться :(', reply_markup=keyboard)

@dp.message_handler(commands=['menu'])
async def menu_handler(message:Message):
	pass

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True, loop=asyncio.get_event_loop())