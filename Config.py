import json
import os

api_key : str = ""
sio_url : str = ""
post_url : str = ""
bot_id : int = 1234567890
groups : list[int]= []


def Load(config_dir: str):
	try:
		config = json.load(open(config_dir, 'r', encoding='UTF-8'))
		global api_key, sio_url, post_url, bot_id, groups
		api_key = config['api_key']
		post_url = config['opq_url']
		sio_url = config['ws_url']
		bot_id = config['bot_qq']
		groups = config['groups']
	except Exception:
		print('Read configuration file failed')
		raise Exception