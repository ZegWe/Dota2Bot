import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import Config
from model.command import Command
from model.logger import logger
from model.message_sender import GroupSender
from model.player import Player
from model.plugin import Plugin

from .DotaDB import DotaDB as DB
from .utils import (generate_message, get_last_match_id_by_short_steamID,
                    steam_id_convert_32_to_64)


class Watcher(Plugin):
	"""
	Dota2战绩自动查询插件
	"""
	
	__name = "DOTA2战绩播报"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__(group_id, sender)
		self.db = DB(group_id)
		self.result : dict[int, list[Player]] = {}
		self.pool = ThreadPoolExecutor(20)
		self.lock = Lock()
		self.playerList : list[Player] = self.db.get_list()
		for player in self.playerList:
			player = self.update_player(player)
		self.running = True
		self.pool.submit(self.update)
		self.commands.append(Command(['查看监视'], [], '： 查看监视列表', self.show_watch))
		self.commands.append(Command(['添加监视'], [str, int, int], '昵称 Steam账号 QQ号： 添加新的监视账号', self.add_watch))
		self.commands.append(Command(['移除监视'], [int], '序号： 移除指定的监视账号', self.remove_watch))
		logger.debug('Dota2 Watcher({}) initialized.'.format(group_id))

	@classmethod
	def get_name(cls):
		return cls.__name

	def update_player(self, player: Player) -> Player:
		# print(time.time())
		try:
			match_id = get_last_match_id_by_short_steamID(player.short_steamID)
		except Exception as e:
			logger.error(repr(e))
			return player
		if match_id == -1:
			return player
		if match_id != player.last_DOTA2_match_ID:
			self.lock.acquire()
			if self.result.get(match_id, 0) != 0:
				self.result[match_id].append(player)
			else:
				self.result.update({match_id: [player]})
			self.lock.release()
			self.db.update_DOTA2_match_ID(player.short_steamID, match_id)
			player.last_DOTA2_match_ID = match_id
		return player

	def update(self):
		logger.debug('Watch Loop started: {}'.format(self.group_id))
		while self.running:
			self.result.clear()
			if len(self.playerList) == 0:
				time.sleep(5)
				continue
			if self.On():
				tmpList = self.pool.map(self.update_player, self.playerList)
				
				self.playerList = list(tmpList)
				for match_id in self.result:
					for message in generate_message(match_id, self.result[match_id]):
						self.sender.send(message)
			for i in range(300):
				if self.running:
					time.sleep(1)
				else:
					break
		logger.debug('Watching Loop exited: {}'.format(self.group_id))

	def shutdown(self):
		self.running = False
		self.pool.shutdown()
		super().shutdown()

	def add_watch(self, nickname: str, shortID: int, qqid: int, user: int):
		if self.db.is_player_stored(shortID):
			logger.warning('Player already watched.')
			self.sender.send('该账号已经存在，请勿重复添加！')
			return
		longID = steam_id_convert_32_to_64(shortID)
		last_match = get_last_match_id_by_short_steamID(shortID)
		self.db.insert_info(shortID, longID, qqid, nickname, last_match)
		self.playerList.append(Player(nickname, qqid, shortID, longID, last_match))
		logger.success('Player information added successfully.')
		self.sender.send('添加监视成功！')

	def remove_watch(self, index: int, user: int):
		try:
			shortID = self.playerList[index - 1].short_steamID
			if self.db.is_player_stored(shortID):
				self.db.delete_info(shortID)
			del self.playerList[index - 1]
		except Exception as e:
			logger.error('Remove Watch Error: {}'.format(repr(e)))
			self.sender.send('移除监视失败！')
		else:
			logger.success('Remove Watch Successfully!')
			self.sender.send('移除监视成功！')

	def show_watch(self, user: int):
		# print(self.playerList)
		if len(self.playerList) == 0:
			m = '没有正在监视的账号！'
			self.sender.send(m)
			return
		m = '以下账号被监视中：'
		for index, player in enumerate(self.playerList):
			m += '\n{}. {}({})'.format(index + 1, player.nickname, player.short_steamID)
		if len(m):
			self.sender.send(m)

def test():
	Config.Load('./config.json')
	DB.connect()
