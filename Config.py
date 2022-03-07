import json

from model.logger import logger, init_logger
from model.dict import CUSTOM_HERO_LIST

api_key: str = ""
sio_url: str = ""
post_url: str = ""
bot_id: int = 1234567890
groups: list[int] = []
debug: bool = False
mdi_url: str = ""
stratz: str = ""


def Load(config_dir: str):
    try:
        config: dict = json.load(open(config_dir, 'r', encoding='UTF-8'))
        global api_key, sio_url, post_url, bot_id, groups, debug, mdi_url, stratz, CUSTOM_HERO_LIST
        api_key = config['api_key']
        sio_url = config['opq_url']
        post_url = sio_url+'/v1/LuaApiCaller'
        bot_id = config['bot_qq']
        groups = config['groups']
        debug = config['debug']
        mdi_url = config['mdi_url']
        stratz = config['stratz']
        init_logger(debug)
        if "dicts" in config.keys():
            with open(config["dicts"], 'r', encoding='UTF-8') as f:
                CUSTOM_HERO_LIST = json.load(f)

    except Exception:
        logger.error('Read configuration file failed')
        raise Exception
