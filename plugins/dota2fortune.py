import datetime
import random

import pytz
from model.command import Command
from model.message_sender import GroupSender
from model.plugin import Plugin
from model.dict import HEROES_LIST_CHINESE as Heroes

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

heroDict : list = [
	'有必选，选必赢！',
	'快去尝试一下吧！',
	'要不要试试呢？'
]

def get_date() -> datetime.date:
	tz = pytz.timezone('Asia/Shanghai')
	return datetime.datetime.now(tz).date()

class Fort:
	def __init__(self, fort: str = "", sentence: str = ""):
		self.fort = fort
		self.sentence = sentence
		self.upd_date = get_date()

class Hero:
	def __init__(self, hero: str = "", sentence: str = ""):
		self.hero = hero
		self.sentence = sentence
		self.upd_date = get_date()

class User:
	def __init__(self, fort: Fort = Fort(), hero: Hero = Hero()) -> None:
		self.fort = fort
		self.hero = hero

class Fortune(Plugin):
	__name = "DOTA2每日运势"
	def __init__(self, group_id: int, sender: GroupSender):
		super().__init__(group_id, sender)
		self.users : dict[int, User] = {}
		self.commands.append(Command(['今日运势', '今天啥运气'], [], '： 显示今日的Dota2运势', self.get_fortune))
		self.commands.append(Command(['幸运英雄', '今天玩点啥', '不知道玩啥', '玩啥好呢'], [], '： 显示今日的Dota2幸运英雄', self.get_hero))

	@classmethod
	def get_name(cls) -> str:
		return cls.__name
	

	def get_hero(self, FromUserId: int) -> None:
		if FromUserId in self.users:
			tmp_user = self.users[FromUserId]
			if not tmp_user.hero or tmp_user.hero.upd_date != get_date():
				tmp = random.sample(Heroes.keys(), 1)[0]
				sentence = random.choice(heroDict)
				tmp_user = User(tmp_user.fort, Hero(Heroes[tmp], sentence))
				self.users[FromUserId] = tmp_user
		else:
			tmp = random.sample(Heroes.keys(), 1)[0]
			sentence = random.choice(heroDict)
			tmp_user = User(hero=Hero(Heroes[tmp], sentence))
			self.users[FromUserId] = tmp_user
		
		m = '[ATUSER({})]的今日幸运英雄是{}，{}'.format(FromUserId, tmp_user.hero.hero, tmp_user.hero.sentence)
		self.sender.send(m)

	def get_fortune(self, FromUserId: int) -> None:
		if FromUserId in self.users:
			tmp_user = self.users[FromUserId]
			if not tmp_user.fort or tmp_user.fort.upd_date != get_date():
				tmp = random.sample(fortuneDict.keys(), 1)[0]
				tmp_user = User(Fort(tmp, random.choice(fortuneDict[tmp])),tmp_user.hero)
				self.users[FromUserId] = tmp_user
		else:
			tmp = random.sample(fortuneDict.keys(), 1)[0]
			tmp_user = User(Fort(tmp, random.choice(fortuneDict[tmp])))
			self.users[FromUserId] = tmp_user

		m = '[ATUSER({})]的今日运势：\n\n'.format(FromUserId)
		m += '{}\n\n'.format(tmp_user.fort.fort)
		m += tmp_user.fort.sentence
		self.sender.send(m)
