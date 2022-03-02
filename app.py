import argparse

import socketio

import Config
import plugins
from model.db import BaseDB
from model.dict import refresh_hero_list
from model.logger import logger
from model.plugmanager import PluginManager

sio = socketio.Client()
managers: dict[int, PluginManager] = {}


@sio.event
def connect():
    logger.success('Connection established.')


@sio.event
def OnGroupMsgs(data):
    message_data = data['CurrentPacket']['Data']
    if message_data['FromUserId'] == Config.bot_id:
        return
    from_group = message_data['FromGroupId']
    if from_group not in managers:
        return
    managers[from_group].handle(message_data)


@sio.event
def OnFriendMsgs(data):
    logger.info('OnFriendMsgs: {}'.format(data))


@sio.event
def OnEvents(data):
    logger.info('OnEvents: {}'.format(data))


@sio.event
def disconnect():
    logger.warning('Disconnected from server')


def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='./config.json')
    args = parser.parse_args()
    Config.Load(args.config)
    refresh_hero_list()
    BaseDB.connect()
    logger.info(str(plugins.PLUGIN_DICT))
    for group in Config.groups:
        managers[group] = PluginManager(group)
        managers[group].add_plugin('DOTA2战绩播报', True)
        managers[group].add_plugin('DOTA2每日运势', True)
        managers[group].add_plugin('DOTA2战绩图', True)
        managers[group].add_plugin('DOTA2公告', True)


if __name__ == "__main__":
    init()
    logger.debug('Connecting to server...')
    sio.connect(Config.sio_url, transports=['websocket'])
    try:
        sio.wait()
    except KeyboardInterrupt:
        for group in managers:
            managers[group].shutdown()
        BaseDB.disconnect()
        logger.info('Say you next time~')
        exit(0)
