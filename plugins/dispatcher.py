import asyncio

from time import time
from aiogram import Bot
from plugins.database import Database
from plugins.compliments import ComplimentsGetter

class Dispatcher:

	def __init__(self,
		loop:asyncio.AbstractEventLoop=asyncio.get_event_loop(),
		database:Database=Database(),
		compliments:ComplimentsGetter=ComplimentsGetter(),
		bot:Bot=None
	):
		self._loop = loop
		self._db = database
		self._cg = compliments
		self._bot = bot

	async def checker(self):
		for rec in self.database:
			self._bot.send_message(
				chat_id=rec['id'],
				text=(await self._cg.get())
			)
			await self._db.set_cd(
				num=time(),
				edited_id=rec['id']
			)