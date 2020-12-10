from .message_sender import GroupSender

class Plugin(object):
	"""
	Plugin Base Class;
	Could not be used directly
	"""
	__name = ""
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__()
		self.group_id = group_id
		self._on = False
		self.sender = sender

	@classmethod
	def get_name(cls):
		return cls.__name

	def Set(self, on: bool):
		self._on = on

	def On(self) -> bool:
		return self._on

	def shutdown(self):
		print('plugin {} shutdown'.format(self.get_name()))

	def handle(self, data: str):
		pass
