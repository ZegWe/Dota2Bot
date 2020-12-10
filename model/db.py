#!/usr/bin/python
# -*- coding: UTF-8 -*-
from os import error
import sqlite3
from .player import Player

class BaseDB:
	"""
	基于sqlite封装的数据库对象
	所有实例共用同一个数据库文件，根据不同群号来区分不同表
	已封装connect和disconnect函数
	"""
	def __init__(self, group_id: int):
		raise SyntaxError
		self.group_id = group_id

	@classmethod
	def connect(cls, db_file: str, name: str):
		"""
		创建数据库文件连接，注意：这是一个类方法！
		"""
		raise SyntaxError
		print('Initializing {}...'.format(name), end='', flush=True)
		cls.conn = sqlite3.connect(db_file, check_same_thread=False)
		cls.c = cls.conn.cursor()
		print('\r', end='', flush=True)
		print('\033[0;32mDatabase {} initialized.\033[0m'.format(name), flush=True)
	@classmethod
	def disconnect(cls, name: str):
		"""
		断开数据库文件连接，注意：这是一个类方法！
		"""
		raise SyntaxError
		cls.conn.close()
		print('{} Closed.'.format(name))
