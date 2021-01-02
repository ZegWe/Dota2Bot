import time
from model.player import Player
from .DotaDB import DotaDB as DB
from model.message_sender import GroupSender
from model.plugin import Plugin
from .DOTA2 import get_last_match_id_by_short_steamID, generate_party_message, generate_solo_message, steam_id_convert_32_to_64
import Config
import re
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

class Watcher(Plugin):
	"""
	Dota2战绩自动查询插件
	"""
	
	_Plugin__name = "DOTA2战绩播报"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__(group_id, sender)
		self.db = DB(group_id)
		self.result = {}
		self.pool = ThreadPoolExecutor(20)
		self.playerList : List[Player] = []
		tmpList = self.db.get_list()
		taskList = []
		for player in tmpList:
			taskList.append(self.pool.submit(self.update_player, player))
		for task in as_completed(taskList):
			self.playerList.append(task.result())
		self.running = True
		t = self.pool.submit(self.update)
		print('Dota2 Watcher({}) initialized.'.format(group_id))


	def update_player(self, player: Player) -> Player:
		# print(time.time())
		try:
			match_id = get_last_match_id_by_short_steamID(player.short_steamID)
		except Exception as e:
			print(repr(e))
			return player
		if match_id != player.last_DOTA2_match_ID:
			if self.result.get(match_id, 0) != 0:
				self.result[match_id].append(player)
			else:
				self.result.update({match_id: [player]})
			
			self.db.update_DOTA2_match_ID(player.short_steamID, match_id)
			player.last_DOTA2_match_ID = match_id
		return player

	def update(self):
		print('Watch Loop started: {}'.format(self.group_id))
		while self.running:
			self.result.clear()
			if len(self.playerList) == 0:
				time.sleep(5)
				continue
			if self.On():
				taskList : List = []
				for player in self.playerList:
					taskList.append(self.pool.submit(self.update_player, player))
				self.playerList.clear()
				for task in as_completed(taskList):
					self.playerList.append(task.result())
				# print('---------')
				for match_id in self.result:
					if len(self.result[match_id]) > 1:
						for message in generate_party_message(match_id, self.result[match_id]):
							self.sender.send(message)
					elif len(self.result[match_id]) == 1:
						for message in generate_solo_message(match_id, self.result[match_id][0]):
							self.sender.send(message)
			time.sleep((24 * 60 * 60) / (100000 / (2 * len(self.playerList))))
		print('Watching Loop exited: {}'.format(self.group_id))

	def shutdown(self):
		self.running = False
		self.pool.shutdown()
		super().shutdown()

	def add_watch(self, nickname, shortID, qqid):
		if self.db.is_player_stored(shortID):
			print('Already added')
			self.sender.send('该账号已经存在，请勿重复添加！')
			return
		longID = steam_id_convert_32_to_64(shortID)
		last_match = get_last_match_id_by_short_steamID(shortID)
		self.db.insert_info(shortID, longID, qqid, nickname, last_match)
		self.playerList.append(Player(nickname, qqid, shortID, longID, last_match))
		print('Player information added successfully')
		self.sender.send('添加监视成功！')

	def remove_watch(self, index: int):
		try:
			shortID = self.playerList[index - 1].short_steamID
		except Exception as e:
			print('Remove Watch Error Index: {}'.format(repr(e)))
			self.sender.send('请输入正确的序号！')
			return
		try:
			if self.db.is_player_stored(shortID):
				self.db.delete_info(shortID)
			del self.playerList[index - 1]
		except Exception as e:
			print('Remove Watch Error: {}'.format(repr(e)))
			self.sender.send('移除监视失败！')
		else:
			print('Remove Watch Successfully!')
			self.sender.send('移除监视成功！')

	def show_watch(self):
		m = '以下账号被监视中：'
		for index, player in enumerate(self.playerList):
			m += '\n{}. {}({})'.format(index + 1, player.nickname, player.short_steamID)
			if index % 8 == 6:
				self.sender.send(m)
				m = ''
		if len(self.playerList) == 0:
			m = '没有正在监视的账号！'
			self.sender.send(m)
			return
		if len(m):
			self.sender.send(m)

	def handle(self, m: str) -> bool:
		if re.match(r'^[！!]查看监视$', m):
			self.show_watch()
			return True
		elif re.match(r'^[!！]移除监视\s+\S+', m):
			try:
				s = re.match(r'^[!！]移除监视\s+\S+', m)[0]
				index = int(re.split(r'\s+', s)[1])
				self.remove_watch(index)
			except Exception as e:
				print('Remove Watch Error Argument: {}'.format(repr(e)))
				self.sender.send('请输入正确的参数！')
			finally: return True
		elif re.match(r'^[!！]添加监视\s+\S+\s+\S+\s+\S+', m):
			try:
				s = re.match(r'^[!！]添加监视\s+\S+\s+\S+\s+\S+', m)[0]
				# print(s)
				_, nickname, steamID, qqid = re.split(r'\s+', s)
				# print(nickname, steamID, qqid)
				self.add_watch(nickname, int(steamID), int(qqid))
			except Exception as e:
				print('Add Watch Error Argument: {}'.format(repr(e)))
				self.sender.send('请输入正确的参数！')
			finally: return True

		return False

def test():
	Config.Load('./config.json')
	DB.connect('playerInfo.db')
