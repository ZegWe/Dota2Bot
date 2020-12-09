import re
import Config
from plugins import PLUGIN_DICT
from .message_sender import GroupSender


class PluginManager(object):
	"""
	Plugin Manager
	"""
	def __init__(self, group_id: int):
		self.group_id = group_id
		self.plugins: [Plugin] = []
		self.sender = GroupSender(Config.post_url, Config.bot_id, group_id)

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


	def add_plugin(self,plugin_name: str):
		new_plugin = PLUGIN_DICT[plugin_name]
		self.plugins.append(new_plugin(self.group_id, self.sender))

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
		except Exception as e:
			print('Enable Plugin Failed: {}'.format(e))
			self.sender.send('启用插件失败！')
		else:
			print('Plugin {} Enabled!'.format(self.plugins[index - 1].get_name()))
			self.sender.send('插件 {} 已启用'.format(self.plugins[index - 1].get_name()))

	def disable_plugin(self, index: int):
		try:
			self.plugins[index - 1].Set(False)
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