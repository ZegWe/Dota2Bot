#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
from .player import Player

class DB:
	def __init__(self, group_id: str):
		print('Initializing database...', end='', flush=True)
		self.group_id = group_id
		if not hasattr(self, 'c'):
			self.connect('playerInfo.db')
		self.c.execute('''CREATE TABLE IF NOT EXISTS `playerInfo-{}`
		(short_steamID INT PRIMARYKEY NOT NULL,
		long_steamID INT NOT NULL,
		nickname CHAR(50) NOT NULL,
		qqid INT NOT NULL,
		last_DOTA2_match_ID INT);
		'''.format(group_id))
		print('\r', end='', flush=True)
		print('\033[0;32mSqlite database initialized.\033[0m', flush=True)

	@classmethod
	def connect(cls, db_file: str):
		cls.conn = sqlite3.connect(db_file, check_same_thread=False)
		cls.c = cls.conn.cursor()

	def get_list(self):
		PLAYER_LIST = []
		cursor = self.c.execute("SELECT * from `playerInfo-{}`".format(self.group_id))
		for row in cursor:
			player_obj = Player(short_steamID=row[0],
								long_steamID=row[1],
								nickname=row[2],
								qqid=row[3],
								last_DOTA2_match_ID=row[4])
			PLAYER_LIST.append(player_obj)
		return PLAYER_LIST

	def update_DOTA2_match_ID(self, short_steamID, last_DOTA2_match_ID):
		self.c.execute("UPDATE `playerInfo-{}` SET last_DOTA2_match_ID='{}' "
				"WHERE short_steamID={}".format(self.group_id, last_DOTA2_match_ID, short_steamID))
		self.conn.commit()

	def insert_info(self, short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID):
		self.c.execute("INSERT INTO `playerInfo-{}` (short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID) "
				"VALUES ({}, {}, {}, '{}', '{}')"
				.format(self.group_id, short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID))
		self.conn.commit()

	def delete_info(self, short_steamID):
		self.c.execute("DELETE FROM `playerInfo-{}` WHERE short_steamID={}".format(self.group_id, short_steamID))
		self.conn.commit()

	def is_player_stored(self, short_steamID: int) -> bool:
		self.c.execute("SELECT * FROM `playerInfo-{}` WHERE short_steamID=={}".format(self.group_id, short_steamID))
		if len(self.c.fetchall()) == 0:
			return False
		return True
