from typing import Hashable, Any

class Storage:

	def __init__(self):
		self.payload = {}

	def get(self, index:Hashable='index') -> Any:
		try: return self.payload[index]
		except: return None

	def set(self, index_name:Hashable='index', element:Any=5) -> None:
		self.payload[index_name] = element

	def delete(self, index:Hashable='index') -> None:
		try: del self.payload[index]
		except: raise IndexError(f'This object ("{index}") not exists')