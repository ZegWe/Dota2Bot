import datetime
import json
import time

import pytz
import requests

from .logger import logger


def get_time() -> datetime.datetime:
	tz = pytz.timezone('Asia/Shanghai')
	return datetime.datetime.now(tz)

class MsgSender:
	__last_time : datetime.datetime = get_time()
	def __init__(self, url: str, qid: int, to: int):
		self.url: str = url
		self.qid: int = qid
		self.to: int = to
		self._data: dict = {}

	def _get_data(self, message: str) -> dict:
		tmp = self._data
		tmp["Content"] = message
		return tmp

	@classmethod
	def get_last_time(cls) -> datetime.datetime:
		return cls.__last_time

	@classmethod
	def set_last_time(cls, time: datetime.datetime):
		cls.__last_time = time

	def send(self, message: str):
		delta = datetime.timedelta(seconds=1.1)
		send_time = get_time()
		if send_time - self.get_last_time() < delta:
			time.sleep((self.get_last_time() + delta - send_time).total_seconds())
		try:
			data = self._get_data(message)
			r = requests.post(self.url + "?qq=" + str(self.qid) + "&funcname=SendMsgV2", json.dumps(data))
			if json.loads(r.text).get('Ret') == 241:
				logger.warning("Message sending failed, resending now...\n{}".format(r.text))
				time.sleep(0.5)
				r = requests.post(self.url + "?qq=" + str(self.qid) + "&funcname=SendMsgV2", json.dumps(data))
			self.set_last_time(get_time())
			if json.loads(r.text).get('Ret') != 0:
				logger.error("Message sending failed.\n{}".format(r.text))
				return
			logger.success("Message sending succeeded.\n{}".format(data))
		except Exception as e:
			logger.error("Post request error.\n{}".format(repr(e)))

class GroupSender(MsgSender):
	def __init__(self, url: str, qid: int, to: int):
		super().__init__(url, qid, to)
		self._data = {
				"ToUserUid": self.to,
				"SendToType": 2,
				"SendMsgType": "TextMsg",
				"Content": ""
			}

class FriendSender(MsgSender):
	def __init__(self, url: str, qid: int, to: int):
		super().__init__(url, qid, to)
		self._data = {
				"ToUserUid": self.to,
				"SendToType": 1,
				"SendMsgType": "TextMsg",
				"Content": ""
			}
