from .message_sender import GroupSender

class Plugin(object):
	"""
	Plugin Base Class;
	Could not be used directly
	"""
	__name = "PluginBaseClass"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__()
		self.group_id : int = group_id
		self._on : bool = False
		self.sender : GroupSender = sender

	@classmethod
	def get_name(cls) -> str:
		return cls.__name

	def Set(self, on: bool):
		self._on = on

	def On(self) -> bool:
		return self._on

	def shutdown(self):
		print('plugin {} shutdown'.format(self.get_name()))

	def handle(self, data: dict):
		pass
