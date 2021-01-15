from model.plugin import Plugin
from model.message_sender import GroupSender
import re
import random
import pytz, datetime

fortuneDict : dict[str, list[str]] = {
	'大吉': [
		'今日宜上分，有果皇带躺',
		'今日宜玩果虚空，果皇附体，神勇无敌',
		'今日宜玩中单，快去和may皇对线',
		'今日宜玩大哥，你就是阿么本么',
	],
	'中吉': [
		'今日宜科研，整活也能打爆对面',
		'今日宜玩影魔，物影一！！！',
		'今日宜天梯，上分之路势不可挡',
	],
	'小吉': [
		'今日宜普匹，胜率随缘，但都能玩得开心',
		'今日宜看翔哥，不会脑溢血 https://www.douyu.com/60937',
	],
	'凶': [
		'今日不宜上分，可能会遇到果皇',
		'今日宜娱乐，欢声笑语中打出gg也未尝不可',
	],
	'大凶': [
		'今日不宜游戏，每把对面都有果皇',
		'今日宜看直播，建议多学点技术再玩游戏 https://www.douyu.com/9999',
	]
}

def get_date() -> datetime.date:
	tz = pytz.timezone('Asia/Shanghai')
	return datetime.datetime.now(tz).date()

class User:
	def __init__(self, fort: str, sentence: str):
		self.fort = fort
		self.sentence = sentence
		self.upd_date = get_date()

class Fortune(Plugin):
	__name = "DOTA2每日运势"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__(group_id, sender)
		self.users : dict[int, User] = {}

	@classmethod
	def get_name(cls) -> str:
		return cls.__name
	
	def handle(self, data: dict) -> bool:
		m = data['Content']
		if re.match(r'^[！!]今日运势$', m):
			message = self.get_fortune(data['FromUserId'])
			self.sender.send(message)
			return True
		return False

	def get_fortune(self, FromUserId) -> str:
		if FromUserId in self.users:
			tmp_user = self.users[FromUserId]
			if tmp_user.upd_date != get_date():
				tmp = random.sample(fortuneDict.keys(), 1)[0]
				tmp_user = User(tmp, random.choice(fortuneDict[tmp]))
				self.users[FromUserId] = tmp_user
		else:
			tmp = random.sample(fortuneDict.keys(), 1)[0]
			tmp_user = User(tmp, random.choice(fortuneDict[tmp]))

		m = '[ATUSER({})] 的今日运势：\n\n'.format(str(FromUserId))
		m += '{}\n\n'.format(tmp_user.fort)
		m += tmp_user.sentence
		return m