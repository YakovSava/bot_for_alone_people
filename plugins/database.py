import asyncio
import aiosqlite

from os.path import join
from typing import AsyncIterator, AsyncContextManager

class Database:

	def __init__(self, loop:asyncio.AbstractEventLoop=asyncio.get_event_loop()):
		self._loop = loop
		self._loop.run_until_complete(self._setter())

	async def _setter(self):
		self.connection = await aiosqlite.connect(join('data', 'data.db'), check_same_thread=False)
		self.connection.row_factory = aiosqlite.Row
		self.cursor = self.connection.cursor()
		await self.cursor.execute('''CREATE TABLE if not exists Users (
	name TEXT,
	id BIGINT,
	compliments_in_day INT
)''')
		await self.connection.commit()

	async def _destructor(self):
		await self.connection.close()
		await self.cursor.close()

	async def get(self, get_id:int=None) -> aiosqlite.Row:
		await self.cursor.execute(f'SELECT * FROM Users WHERE id = {get_id}')
		return await self.cursor.fetchone()

	async def edit_cid(self, edit_id:int=None, cid:int=5) -> None:
		await self.cursor.execute(f'UPDATE Users SET compliments_in_day = {cid} WHERE id = {edit_id}')
		await self.connection.commit()

	async def reg(self, data:dict={'id': 666, 'name': 'NameExample', 'cid': 5}) -> None:
		await self.cursor.execute('INSERT INTO Users VALUES (?,?,?)', (data['name'], data['id'], data['cid']))
		await self.connection.commit()

	async def xget_all(self) -> tuple:
		await self.cursor.execute('SELECT * FROM Users')
		return await self.cursor.fetchall()

	async def get_all(self) -> aiosqlite.Row:
		await self.cursor.execute('SELECT * FROM Users')
		for record in (await self.cursor.fetchall()):
			yield record

	async def __aenter__(self, *args, **kwargs) -> AsyncContextManager: return self
	async def __aexit__(self) -> None: await self.connection.commit()
	async def __aiter__(self) -> AsyncIterator: return self.get_all

	def __del__(self):
		self._loop.run_until_complete(self._destructor())