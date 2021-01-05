import time
import socketio
import argparse
import Config
from model.plugmanager import PluginManager, PluginDB
from plugins.dota2watcher.DotaDB import DotaDB
import threading

sio = socketio.Client()
managers : dict[int, PluginManager] = {}

@sio.event
def connect():
	print('\rConnection established.', flush=True)

@sio.event
def OnGroupMsgs(data):
	message_data = data['CurrentPacket']['Data']
	from_group = message_data['FromGroupId']
	if from_group not in managers:
		return
	manager = managers[from_group]
	manager.handle(message_data)

@sio.event
def OnFriendMsgs(data):
	print('OnFriendMsgs: ', data)

@sio.event
def OnEvents(data):
	print('OnEvents: ', data)

@sio.event
def disconnect():
    print('disconnected from server')

def init():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', default='./config.json')
	args = parser.parse_args()
	Config.Load(args.config)
	for group in Config.groups:
		managers[group] = PluginManager(group)
		managers[group].add_plugin('DOTA2战绩播报', True)
		managers[group].add_plugin('DOTA2每日运势', True)

@sio.event
def GetWebConn(data):
	sio.emit('GetWebConn', data)

def heartbeat():
	while sio_connected:
		for i in range(50):
			time.sleep(1)
			if not sio_connected:
				break
		if not sio_connected:
			break
		if not sio.connected:
			continue
		sio.emit('GetWebConn', Config.bot_id)

if __name__ == "__main__":
	init()
	print('Connecting to server...', end='', flush=True)
	sio.connect(Config.sio_url, transports=['websocket'])
	sio_connected = True
	t = threading.Thread(target=heartbeat)
	t.start()
	try:
		sio.wait()
	except KeyboardInterrupt:
		sio_connected = False
		for group in managers:
			managers[group].shutdown()
		PluginDB.disconnect(PluginDB.get_name())
		DotaDB.disconnect(DotaDB.get_name())
		t.join()
		print('Say you next time~')
		exit(0)