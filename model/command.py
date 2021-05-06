import re
from .logger import logger

class Command:
	"""
	:commands: Command string list

	:return_list: Type of the command args. (e.g. [int, str])

	:tip: Tips which would be shown in help
	
	:func: The function you want to call by the command
	"""
	def __init__(self, commands: list[str], return_list: list, tip: str, func) -> None:
		self.commands = commands
		self.return_list = return_list
		self.func  = func
		self.help = tip

	def run(self, m: str, user: int) -> bool:
		for command in self.commands:
			try:
				args, ok = get_command(command, self.return_list, m)
				if ok:
					self.func(*args, user)
					return True
			except Exception as e:
				logger.error(e)
		return False

def get_command(command: str, return_list: list, s: str) -> tuple[list, bool]:
	ret = []
	r = re.compile(r'^[!！]{}(\s+\S+)*'.format(command))
	if not r.match(s):
		return [], False
	s = str(r.match(s)[0])
	args = re.split(r'\s+', s)[1:]
	if len(args) < len(return_list):
		logger.error('No enough args')
		return [], False
	for i, t in enumerate(return_list):
		try:
			ret.append(t(args[i]))
		except Exception as e:
			logger.error(e)
			return [], False
	return ret, True
