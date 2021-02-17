import sys

from loguru import logger

def init_logger(debug: bool):
	logger.remove()
	if debug:
		logger.add(sys.stdout, level='DEBUG', format='<level>{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {name}:{function}:{line} - {message}</level>')
	else:
		logger.add(sys.stdout, level='INFO', format='<level>{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}</level>')

init_logger(False)