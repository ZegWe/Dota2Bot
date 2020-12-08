import json
import os

api_key = ""
sio_url = ""
post_url = ""
bot_id = 1234567890
groups = []

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
		raise (Exception)