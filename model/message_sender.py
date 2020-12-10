#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import time

class MsgSender:
	def __init__(self, url: str, qid: int, to: int):
		self.url: str = url
		self.qid: int = qid
		self.to:int = to
		self.last_send_time:float = 0
		self._data: dict = {}

	def _get_data(self, message: str) -> dict:
		tmp = self._data
		tmp["Content"] = message
		return tmp

	def send(self):
		print("Could not send message, You should implement this method yourself")

class GroupSender(MsgSender):
	def __init__(self, url: str, qid: int, to: int):
		super().__init__(url, qid, to)
		self._data = {
				"ToUserUid": self.to,
				"SendToType": 2,
				"SendMsgType": "TextMsg",
				"Content": ""
			}

	def send(self, message: str):
		if time.time() - self.last_send_time < 1.1:
			time.sleep(1.1 - time.time() + self.last_send_time)
		try:
			data = self._get_data(message)
			r = requests.post(self.url + "?qq=" + str(self.qid) + "&funcname=SendMsgV2", json.dumps(data))
			if json.loads(r.text).get('Ret') == 241:
				time.sleep(0.5)
				r = requests.post(self.url + "?qq=" + str(self.qid) + "&funcname=SendMsgV2", json.dumps(data))
			last_send_time = time.time()
			print(data)
			if json.loads(r.text).get('Ret') != 0:
				print("message sending failed.")
				print(r.text)
				return
			print("message sending succeeded")
		except Exception as e:
			print(e)
			print("post request error")

class FriendSender(MsgSender):
	def __init__(self, url: str, qid: int, to: int):
		super().__init__(url, qid, to)
		self._data = {
				"ToUserUid": self.to,
				"SendToType": 1,
				"SendMsgType": "TextMsg",
				"Content": ""
			}

	def sendGroup(self, message: str):
		data = self._get_data(message)
		if time.time() - self.last_send_time < 1.1:
			time.sleep(1.1 - time.time() + self.last_send_time)
		try:
			r = requests.post(self.url + "?qq=" + str(self.qid) + "&funcname=SendMsgV2", json.dumps(data))
			last_send_time = time.time()
			print(data)
			if json.loads(r.text).get('Ret') != 0:
				print("message sending failed.")
				print(r.text)
				return
			print("message sending succeeded")
		except Exception as e:
			print(e)
			print("post request error")
