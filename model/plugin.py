from .logger import logger
from .message_sender import GroupSender
from .command import Command

class Plugin(object):
	"""
	Plugin Base Class;
	Could not be used directly
	"""
	__name = "PluginBaseClass"
	def __init__(self, group_id: int, sender: GroupSender):
		self.group_id : int = group_id
		self._on : bool = False
		self.sender : GroupSender = sender
		self.commands : list[Command] = []

	@classmethod
	def get_name(cls) -> str:
		return cls.__name

	def Set(self, on: bool):
		self._on = on

	def On(self) -> bool:
		return self._on

	def shutdown(self):
		logger.debug('Plugin {} shutdown.'.format(self.get_name()))

	def show_help(self):
		m = '{}：'.format(self.get_name())
		for com in self.commands:
			m += '\n · {} {}'.format(com.command, com.help)
		self.sender.send(m)

	def handle(self, data: dict):
		m = data['Content']
		user = int(data['FromUserId'])
		for com in self.commands:
			if com.run(m, user):
				return True
		return False
