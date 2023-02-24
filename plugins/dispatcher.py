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
		while True:
			send_compliment = [rec['id'] async for rec in self._db.get_all() if (time() - rec['await'] < (24*60*60) / rec['compliments_in_day'])]
			await asyncio.gather(*[
				self._bot.send_message(
					chat_id=id_,
					text=(await self._cg.get())
				)
				for id_ in send_compliment
			])
			for id_ in send_compliment:
				await self._db.set_cd(
					num=time(),
					edited_id=id_
				)
			await asyncio.sleep(60*60)