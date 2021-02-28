import re
from .logger import logger

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
