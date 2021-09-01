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

		self._data : dict = {
				"ToUserUid": self.to,
			}

	@classmethod
	def get_last_time(cls) -> datetime.datetime:
		return cls.__last_time

	@classmethod
	def set_last_time(cls, time: datetime.datetime):
		cls.__last_time = time

	def send(self, message: str):
		tmp = self._data.copy()
		tmp["SendMsgType"] = "TextMsg"
		tmp["Content"] = message
		self.send_data(tmp)

	def send_image_by_url(self, url: str, msg: str = ""):
		tmp = self._data.copy()
		tmp["SendMsgType"] = "PicMsg"
		tmp["PicUrl"] = url
		tmp["Content"] = msg
		self.send_data(tmp)

	def send_image_by_base64(self, base64_data: str, msg: str = ""):
		tmp = self._data.copy()
		tmp["SendMsgType"] = "PicMsg"
		tmp["PicBase64Buf"] = base64_data
		tmp["Content"] = msg
		self.send_data(tmp)

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
		self._data["SendToType"] = 2

class FriendSender(MsgSender):
	def __init__(self, url: str, qid: int, to: int):
		super().__init__(url, qid, to)
		self._data["SendToType"] = 1