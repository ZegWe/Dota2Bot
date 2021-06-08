import json

from model.logger import logger, init_logger
from model.dict import HEROES_LIST_CHINESE

api_key : str = ""
sio_url : str = ""
post_url : str = ""
bot_id : int = 1234567890
groups : list[int]= []
debug : bool = False

def Load(config_dir: str):
	try:
		config : dict = json.load(open(config_dir, 'r', encoding='UTF-8'))
		global api_key, sio_url, post_url, bot_id, groups, debug
		api_key = config['api_key']
		sio_url = config['opq_url']
		post_url = sio_url+'/v1/LuaApiCaller'
		bot_id = config['bot_qq']
		groups = config['groups']
		debug = config['debug']
		init_logger(debug)
		if "dicts" in config.keys():
			with open(config["dicts"], 'r', encoding='UTF-8') as f:
				dicts = json.load(f)
				replace(dicts)
	except Exception:
		logger.error('Read configuration file failed')
		raise Exception

def replace(dicts: dict):
	for k, v in HEROES_LIST_CHINESE.items():
		if v in dicts:
			HEROES_LIST_CHINESE[k] = dicts[v]