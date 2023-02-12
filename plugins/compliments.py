import asyncio

from googletrans import Translator
from aiohttp import ClientSession

class ComplimentsGetter:

	def __init__(self, loop:asyncio.AbstractEventLoop=asyncio.get_event_loop()):
		self.loop = loop
		self.translator = Translator()
		self.loop.run_until_complete(self._construct())

	async def _construct(self):
		self.session = ClientSession()

	async def get(self):
		async with self.session.get('https://complimentr.com/api') as resp:
			if resp.status == 200:
				data = await resp.json()
		text = self.translator.translate(data['compliment'], dest='ru')
		return text.text

	def __del__(self):
		self.loop.run_until_complete(self.session.close())
		self.loop.close()