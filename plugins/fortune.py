from model.plugin import Plugin
from model.message_sender import GroupSender
import re
from typing import Dict, List
import random

fortuneDict : Dict[str, List[str]] = {
	'上上签': [
		'今日宜上分，有果皇带躺'
	],
	'上签': [
		'今日宜科研，整活也能打爆对面',
		'今日宜玩影魔，物影一！！！',
		'今日宜天梯，上分之路势不可挡'
	],
	'中签': [
		'今日宜普匹，胜率随缘，但都能玩得开心',
		'今日宜看翔哥，不会脑溢血 https://www.douyu.com/60937'
	],
	'下签': [
		'今日不宜上分，可能会遇到果皇',
		'今日宜娱乐，欢声笑语中打出gg也未尝不可'
	],
	'下下签': [
		'今日不宜游戏，每把对面都有果皇',
		'今日宜看直播，建议多学点技术再玩游戏 https://www.douyu.com/9999'
	]
}

class Fortune(Plugin):
	__name = "DOTA2每日运势"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__(group_id, sender)

	@classmethod
	def get_name(cls):
		return cls.__name
	
	def handle(self, data: dict):
		m = data['Content']
		if re.match(r'^[！!]今日运势$', m):
			message = self.get_fortune(data['FromUserId'])
			self.sender.send(message)
			return True
		return False

	def get_fortune(self, FromUserId) -> str:
		m = '[ATUSER({})] 的今日运势：\n\n'.format(str(FromUserId))
		tmp = random.sample(fortuneDict.keys(), 1)[0]
		m += '{}\n\n'.format(tmp)
		m += random.choice(fortuneDict[tmp])
		return m