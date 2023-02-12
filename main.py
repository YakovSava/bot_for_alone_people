import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.typing import Message, ReplyKeyboardMarkup, KeyboardButton
from config import token

bot = Bot(token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_handler(message:Message):
	await message.answer('Привет, солнышко!\nКак твои дела? Прости пожалуйста, но что бы пользоваться мной тебе надо будет зарегестрирвоаться :(')