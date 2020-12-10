from model.plugin import Plugin
import re
import Config
from plugins import PLUGIN_DICT
from .message_sender import GroupSender
from typing import List, Dict
import sqlite3

class PluginManager(object):
	"""
	Plugin Manager
	"""
	def __init__(self, group_id: int):
		self.group_id = group_id
		self.plugins: List[Plugin] = []
		self.sender = GroupSender(Config.post_url, Config.bot_id, group_id)
		self.db = PluginDB(group_id)
		pluginlist = self.db.get_list()
		for plugin_name in pluginlist:
			new_plugin : Plugin = PLUGIN_DICT[plugin_name](group_id, self.sender)
			new_plugin.Set(pluginlist[plugin_name])
			self.plugins.append(new_plugin)

	def handle(self, data: dict):
		m = data['Content']
		if re.match(r'^[！!]插件列表$', m) or re.match(r'^[！!]启用插件$', m) or re.match(r'^[！!]禁用插件$', m):
			self.show_plugins()
			return
		elif re.match(r'^[！!]启用插件\s+\S+', m):
			try:
				s = re.match(r'^[！!]启用插件\s+\S+', m)[0]
				index = int(re.split(r'\s+', s)[1])
				self.enable_plugin(index)
			except TypeError as e:
				print('Argument Error: {}'.format(e))
				self.sender.send('请输入正确的参数！')
			return
		elif re.match(r'^[！!]禁用插件\s+\S+', m):
			try:
				s = re.match(r'^[！!]禁用插件\s+\S+', m)[0]
				index = int(re.split(r'\s+', s)[1])
				self.disable_plugin(index)
			except TypeError as e:
				print('Argument Error: {}'.format(e))
				self.sender.send('请输入正确的参数！')
			return
		else:
			for plugin in self.plugins:
				if plugin.On():
					if plugin.handle(m):
						return
		if re.match(r'^[!！]', m):
			self.sender.send('未找到此命令！')


	def add_plugin(self, plugin_name: str, status: bool):
		if PLUGIN_DICT.get(plugin_name, 0) == 0:
			return
		for plugin in self.plugins:
			print(plugin_name, plugin.get_name())
			if plugin.get_name() == plugin_name:
				return
		new_plugin = PLUGIN_DICT[plugin_name](self.group_id,self.sender)
		new_plugin.Set(status)
		self.plugins.append(new_plugin)
		self.db.insert_info(plugin_name, status)

	def show_plugins(self):
		m = '插件列表：'
		for index, plugin in enumerate(self.plugins):
			m += '\n{}. {}: {}'.format(index + 1, plugin.get_name(), '✅' if plugin.On() else '❌')
		if len(self.plugins) == 0:
			m = '没有可用插件！'
		self.sender.send(m)

	def enable_plugin(self, index: int):
		try:
			self.plugins[index - 1].Set(True)
			self.db.update_info(self.plugins[index-1].get_name(), True)
		except Exception as e:
			print('Enable Plugin Failed: {}'.format(e))
			self.sender.send('启用插件失败！')
		else:
			print('Plugin {} Enabled!'.format(self.plugins[index - 1].get_name()))
			self.sender.send('插件 {} 已启用'.format(self.plugins[index - 1].get_name()))

	def disable_plugin(self, index: int):
		try:
			self.plugins[index - 1].Set(False)
			self.db.update_info(self.plugins[index-1].get_name(), False)
		except Exception as e:
			print('Disable Plugin Failed: {}'.format(e))
			self.sender.send('禁用插件失败！')
		else:
			print('Plugin {} Disabled!'.format(self.plugins[index - 1].get_name()))
			self.sender.send('插件 {} 已禁用'.format(self.plugins[index-1].get_name()))

	def shutdown(self):
		for plugin in self.plugins:
			plugin.shutdown()
		print('manager({}) shutdown'.format(self.group_id))

class PluginDB():
	"""
	存储插件信息的数据库
	"""
	
	__name = "PluginDB"
	def __init__(self, group_id: int):
		self.group_id = group_id
		if not hasattr(self, 'c'):
			self.connect('pluginInfo.db')
		self.c.execute("""
		CREATE TABLE IF NOT EXISTS `pluginInfo-{}` 
		(plugin_name CHAR(50) PRIMARY KEY NOT NULL,
		status BOOLEAN NOT NULL);
		""" .format(self.group_id))
		self.conn.commit()
		
	@classmethod
	def connect(cls, db_file: str):
		"""
		创建数据库文件连接，注意：这是一个类方法！
		"""
		print('Initializing {}...'.format(cls.__name), end='', flush=True)
		cls.conn = sqlite3.connect(db_file, check_same_thread=False)
		cls.c = cls.conn.cursor()
		print('\r', end='', flush=True)
		print('\033[0;32mDatabase {} initialized.\033[0m'.format(cls.__name), flush=True)

	@classmethod
	def disconnect(cls, name: str):
		"""
		断开数据库文件连接，注意：这是一个类方法！
		"""
		cls.conn.close()
		print('{} Closed.'.format(name))

	@classmethod
	def get_name(cls):
		return cls.__name

	def get_list(self):
		plugindict : Dict[str, bool] = {}
		cursor = self.c.execute('SELECT * FROM `pluginInfo-{}`'.format(self.group_id))
		for row in cursor:
			plugindict.update({row[0]: row[1]})
		return plugindict

	def insert_info(self, plugin_name: str, status: bool):
		com = "INSERT INTO `pluginInfo-{}` (plugin_name, status) \
				VALUES ('{}', {})".format(self.group_id, plugin_name, status)
		self.c.execute(com)
		self.conn.commit()

	def update_info(self, plugin_name: str, status: bool):
		self.c.execute("UPDATE `pluginInfo-{}` SET status={} WHERE plugin_name='{}'"
			.format(self.group_id, status, plugin_name))
		self.conn.commit()