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

	async def get(self) -> str:
		async with self.session.get('https://8768zwfurd.execute-api.us-east-1.amazonaws.com/v1/compliments') as resp:
			data = (await resp.read()).decode()
		text = self.translator.translate(data[1:-1], dest='ru')
		return text.text

	def __del__(self):
		self.loop.run_until_complete(self.session.close())
		self.loop.close()