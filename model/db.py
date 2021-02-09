#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
from threading import Lock

class BaseDB:
	"""
	基于sqlite封装的数据库对象
	所有实例共用同一个数据库文件，根据不同群号来区分不同表
	已封装connect和disconnect函数
	使用数据库时请务必加上线程锁
	"""
	__filename : str = "botInfo.db"
	def __init__(self, group_id: int):
		self.group_id = group_id

	@classmethod
	def connect(cls):
		"""
		创建数据库文件连接，注意：这是一个类方法！
		"""
		cls.conn = sqlite3.connect(cls.__filename, check_same_thread=False)
		cls.c = cls.conn.cursor()
		cls.lock = Lock()
		print('\033[0;32mDatabase initialized.\033[0m')

	@classmethod
	def disconnect(cls):
		"""
		断开数据库文件连接，注意：这是一个类方法！
		"""
		cls.conn.close()
		print('Database Closed.')
