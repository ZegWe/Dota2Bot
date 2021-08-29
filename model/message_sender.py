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
		self._image_data: dict = {}

	def _get_data(self, message: str) -> dict:
		tmp = self._data
		tmp["Content"] = message
		return tmp

	def _get_image_data(self, url: str) -> dict:
		tmp = self._image_data
		tmp["PicUrl"] = url
		return tmp


	@classmethod
	def get_last_time(cls) -> datetime.datetime:
		return cls.__last_time

	@classmethod
	def set_last_time(cls, time: datetime.datetime):
		cls.__last_time = time

	def send(self, message: str):
		data = self._get_data(message)
		self.send_data(data)

	def send_image(self, url: str):
		data = self._get_image_data(url)
		self.send_data(data)

	def send_data(self, data: dict):
		delta = datetime.timedelta(seconds=1.1)
		send_time = get_time()
		if send_time - self.get_last_time() < delta:
			time.sleep((self.get_last_time() + delta - send_time).total_seconds())
		try:
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
			logger.error("Post request error: {}\n{}".format(repr(e), data))

class GroupSender(MsgSender):
	def __init__(self, url: str, qid: int, to: int):
		super().__init__(url, qid, to)
		self._data = {
				"ToUserUid": self.to,
				"SendToType": 2,
				"SendMsgType": "TextMsg",
				"Content": ""
			}

		self._image_data = {
				"ToUserUid": self.to,
				"SendToType": 2,
				"SendMsgType": "PicMsg",
				"PicUrl": ""
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

		self._image_data = {
				"ToUserUid": self.to,
				"SendToType": 1,
				"SendMsgType": "PicMsg",
				"PicUrl": ""
			}