import time
import json
from model.player import Player
from model.db import DB
from model.message_sender import GroupSender
from model.plugin import Plugin
from .DOTA2 import get_last_match_id_by_short_steamID, generate_party_message, generate_solo_message, steam_id_convert_32_to_64
import Config
import asyncio
import socketio
import re


class Watcher(Plugin):
	"""
	Dota2战绩自动查询插件
	"""
	
	_Plugin__name = "DOTA2战绩播报"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__(group_id, sender)
		self.db = DB(group_id)
		self.PLAYER_LIST = self.db.get_list()
		self.result = {}

	async def _update_player(self, player: Player):
		try:
			match_id = get_last_match_id_by_short_steamID(player.short_steamID)
		except Exception:
			print(Exception)
			return
		if match_id != player.last_DOTA2_match_ID:
			if self.result.get(match_id, 0) != 0:
				self.result[match_id].append(player)
			else:
				self.result.update({match_id: [player]})
			
			self.db.update_DOTA2_match_ID(player.short_steamID, match_id)
			player.last_DOTA2_match_ID = match_id
		return player


	async def _update(self):
		while self.on():
			self.result.clear()
			if len(self.PLAYER_LIST) == 0:
				time.sleep(10)
				continue
			for player in self.PLAYER_LIST:
				player = await self._update_player(player)
			for match_id in self.result:
				if len(self.result[match_id]) > 1:
					for message in generate_party_message(match_id, self.result[match_id]):
						self.sender.send(message)
				elif len(self.result[match_id]) == 1:
					for message in generate_solo_message(match_id, self.result[match_id][0]):
						self.sender.send(message)
			time.sleep((24*60*60)/(100000/(2*len(self.PLAYER_LIST))))

	def Set(self, on: bool):
		if on == self._on:
			return
		self._on = on
		if on:
			asyncio.set_event_loop(asyncio.new_event_loop())
			socketio.AsyncClient().start_background_task(self._update)

	def add_watch(self, nickname, shortID, qqid):
		if self.db.is_player_stored(shortID):
			print('Already added')
			self.sender.send('该玩家已经存在，请勿重复添加')
			return
		longID = steam_id_convert_32_to_64(shortID)
		last_match = get_last_match_id_by_short_steamID(shortID)
		self.db.insert_info(shortID, longID, qqid, nickname, last_match)
		self.PLAYER_LIST.append(Player(nickname, qqid, shortID, longID, last_match))
		print('Player information added successfully')
		self.sender.send('添加玩家成功')

	def show_watch(self):
		m = '以下账号正在监视中：'
		for index, player in enumerate(self.PLAYER_LIST):
			m += '\n{}. {}({})'.format(index + 1, player.nickname, player.short_steamID)
		
		if len(self.PLAYER_LIST) == 0:
			m = '没有正在监视的玩家！'
		self.sender.send(m)

	def handle(self, m: str) -> bool:
		if re.match(r'^[！!]查看玩家$', m):
			self.show_watch()
			return True
		return False

def test():
	Config.Load('./config.json')
	DB.connect('playerInfo.db')
