import datetime
import random

import Config
import pytz
import requests
from model.account import Account
from model.dict import *
from model.error import DOTA2HTTPError
from model.logger import logger
from model.match import MatchPlayer, get_match_detail

from .messages import Messages

# 异常处理

def steam_id_convert_32_to_64(short_steamID: int) -> int:
    return short_steamID + 76561197960265728

def steam_id_convert_64_to_32(long_steamID: int) -> int:
    return long_steamID - 76561197960265728

def get_last_match_id_by_short_steamID(short_steamID: int) -> int:
    # get match_id
	url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1?key={}' \
          '&account_id={}&matches_requested=1'.format(Config.api_key, short_steamID)
	try:
		response = requests.get(url)
	except requests.RequestException:
		logger.error(DOTA2HTTPError("Requests Error", url))
		return -1
	if response.status_code == 429:
		try:
			response = requests.get(url)
		except requests.RequestException:
			logger.error(DOTA2HTTPError("Requests Error", url))
			return -1
	if response.status_code >= 400:
		if response.status_code == 401:
			logger.error(DOTA2HTTPError("Unauthorized request 401. Verify API key.", url))
			return -1
		if response.status_code == 429:
			logger.error(DOTA2HTTPError('429 Too Many Requests!', url))
			return -1
		if response.status_code == 503:
			logger.error(DOTA2HTTPError(
				"The server is busy or you exceeded limits. Please wait 30s and try again.", url))
			return -1
		logger.error(DOTA2HTTPError(
			"Failed to retrieve data: %s. URL: %s" % (response.status_code, url)))
		return -1

	match = response.json()
	try:
		match_id = match["result"]["matches"][0]["match_id"]
	except KeyError:
		logger.error(DOTA2HTTPError("Response Error: Key Error", url))
		return -1
	except IndexError:
		logger.error(DOTA2HTTPError("Response Error: Index Error", url))
		return -1
	return match_id


# 接收某局比赛的玩家列表, 生成战报
# 参数为玩家对象列表和比赛ID
def generate_message(match_id: int, accounts: list[Account]) -> list[str]:
	logger.debug('generating...')
	try:
		detail = get_match_detail(match_id, Config.api_key)
	except DOTA2HTTPError as e:
		logger.error(e)
		return ["DOTA2战报生成失败"]

	if detail.mode in [15, 19]:  # 各种活动模式不通报
		return []
	mode = GAME_MODE[detail.mode] if detail.mode in GAME_MODE else '未知'

	lobby = LOBBY[detail.typ] if detail.typ in LOBBY else '未知'
	solo = True if len(accounts) == 1 else False
    # 更新玩家对象的比赛信息
	players : list[MatchPlayer] = []
	for player in detail.players:
		for account in accounts:
			if player.account_id == account.short_steamID:
				player.account = account
				players.append(player)
				break
    # 队伍信息
	scores = detail.scores
	radiant = players[0].radiant
	if not radiant: scores.reverse()

	team_damage = sum([x.damage for x in detail.players if x.radiant == radiant])
	team_kills = sum([x.kills for x in detail.players if x.radiant == radiant])
	team_deaths = sum([x.deaths for x in detail.players if x.radiant == radiant])

	win = radiant == detail.radiant_win

	nicks = [x.account.nickname for x in players if x.account]

	print_str = ", ".join(nicks)

	top_kda = max([x.kda for x in players])

	if (win and top_kda > 10) or (not win and top_kda > 6):
		postive = 1
	elif (win and top_kda < 4) or (not win and top_kda < 1):
		postive = 0
	else:
		postive = random.randint(0, 1)

	print_str = random.choice(Messages[solo*4+win*2+postive]).format(print_str)

	start_time = datetime.datetime.fromtimestamp(detail.start_time, tz=pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
	print_str += "\n开始时间: {}".format(start_time)
	print_str += "\n持续时间: {:.0f}:{:02.0f}".format(
		detail.duration / 60, detail.duration % 60)
	print_str += "\n游戏模式: [{}/{}]".format(mode, lobby)
	print_str += "\n总比分： {}:{}".format(scores[0], scores[1])
	print_str += "\n战绩详情: https://www.dotabuff.com/matches/{}".format(match_id)
	for player in players:
		hero = HEROES_LIST_CHINESE[player.hero] if player.hero in HEROES_LIST_CHINESE else '不知道什么鬼'
		persona, kda = player.persona, player.kda
		last_hits, denies = player.last_hits, player.denies
		damage = player.damage
		kills, deaths, assists = player.kills, player.deaths, player.assists
		gpm, xpm = player.gpm, player.xpm

		damage_rate = 0 if team_damage == 0 else (100 * (float(damage) / team_damage))
		participation = 0 if team_kills == 0 else (100 * float(kills + assists) / team_kills)
		deaths_rate = 0 if team_deaths == 0 else (100 * float(deaths) / team_deaths)
		print_str += "\n\n{}使用{}\nKDA: {:.2f}[{}/{}/{}]\nGPM/XPM: {}/{}\n补刀数: {}/{}\n总伤害: {}({:.2f}%)\n参战率: {:.2f}%\n参葬率: {:.2f}%" \
			.format(persona, hero, kda, kills, deaths, assists, gpm, xpm, last_hits, denies, damage, damage_rate, participation, deaths_rate)
	return [print_str]
