from model.db import BaseDB
from model.player import Player
import sqlite3
from typing import List

class DotaDB():
	"""
	基于BaseDB的DOta2战绩数据库，以供Dota2Watcher插件使用
	"""
	__name = "Dota2 Player Info DB"
	def __init__(self, group_id: int):
		"""
		:param group_id: Watcher提供的群号
		"""
		self.group_id = group_id
		if not hasattr(self, 'c'):
			self.connect('playerInfo.db')
		self.c.execute('''
		CREATE TABLE IF NOT EXISTS `playerInfo-{}`
		(short_steamID INT PRIMARYKEY NOT NULL,
		long_steamID INT NOT NULL,
		nickname CHAR(50) NOT NULL,
		qqid INT NOT NULL,
		last_DOTA2_match_ID INT);
		''' .format(group_id))
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

	def get_list(self) -> list:
		"""
		查询数据库中储存的所有玩家信息，返回一个player列表

		$return: 数据库中的player列表
		"""
		playerList : List[Player]= []
		cursor = self.c.execute("SELECT * from `playerInfo-{}`".format(self.group_id))
		for row in cursor:
			player_obj = Player(short_steamID=row[0],
								long_steamID=row[1],
								nickname=row[2],
								qqid=row[3],
								last_DOTA2_match_ID=row[4])
			playerList.append(player_obj)
		return playerList

	def update_DOTA2_match_ID(self, short_steamID, last_DOTA2_match_ID):
		for _ in range(3):
			try:
				self.c.execute("UPDATE `playerInfo-{}` SET last_DOTA2_match_ID='{}' "
					"WHERE short_steamID={}".format(self.group_id, last_DOTA2_match_ID, short_steamID))
			except Exception as e:
				print(repr(e))
			else:
				break
		self.conn.commit()

	def insert_info(self, short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID):
		for _ in range(3):
			try:
				self.c.execute("INSERT INTO `playerInfo-{}` (short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID) "
					"VALUES ({}, {}, {}, '{}', '{}')"
					.format(self.group_id, short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID))
			except Exception as e:
				print(repr(e))
			else:
				break
		self.conn.commit()

	def delete_info(self, short_steamID):
		for _ in range(3):
			try:
				self.c.execute("DELETE FROM `playerInfo-{}` WHERE short_steamID={}".format(self.group_id, short_steamID))
			except Exception as e:
				print(repr(e))
			else:
				break
		self.conn.commit()

	def is_player_stored(self, short_steamID: int) -> bool:
		self.c.execute("SELECT * FROM `playerInfo-{}` WHERE short_steamID=={}".format(self.group_id, short_steamID))
		if len(self.c.fetchall()) == 0:
			return False
		return True
