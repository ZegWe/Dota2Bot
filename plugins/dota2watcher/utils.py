import datetime
import random

import Config
import pytz
import requests
from model.dict import *
from model.logger import logger
from model.player import Player

from .messages import Messages


# 异常处理
class DOTA2HTTPError(Exception):
    pass

def steam_id_convert_32_to_64(short_steamID: int) -> int:
    return short_steamID + 76561197960265728

def steam_id_convert_64_to_32(long_steamID: int) -> int:
    return long_steamID - 76561197960265728

# 根据slot判断队伍, 返回1为天辉, 2为夜魇
def get_team_by_slot(slot: int) -> int:
    if slot < 100:
        return 1
    else:
        return 2

def get_last_match_id_by_short_steamID(short_steamID: int) -> int:
    # get match_id
	url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v001/?key={}' \
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


def get_match_detail_info(match_id: int) -> dict:
    # get match detail
    url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/' \
          '?key={}&match_id={}'.format(Config.api_key, match_id)
    try:
        response = requests.get(url)
    except requests.RequestException:
        raise DOTA2HTTPError("Requests Error.")
    if response.status_code >= 400:
        if response.status_code == 401:
            raise DOTA2HTTPError("Unauthorized request 401. Verify API key.")
        if response.status_code == 503:
            raise DOTA2HTTPError(
                "The server is busy or you exceeded limits. Please wait 30s and try again.")
        raise DOTA2HTTPError(
            "Failed to retrieve data: %s. URL: %s" % (response.status_code, url))

    match = response.json()
    try:
        match_info = match["result"]
    except KeyError:
        raise DOTA2HTTPError("Response Error: Key Error")
    except IndexError:
        raise DOTA2HTTPError("Response Error: Index Error")

    return match_info

# 接收某局比赛的玩家列表, 生成战报
# 参数为玩家对象列表和比赛ID
def generate_message(match_id: int, player_list: list[Player]) -> list[str]:
	try:
		match = get_match_detail_info(match_id=match_id)
	except DOTA2HTTPError as e:
		logger.error(e)
		return ["DOTA2战报生成失败"]

    # 比赛模式
	mode_id = match["game_mode"]
	if mode_id in [15]:  # 各种活动模式不通报
		return []
	mode = GAME_MODE[mode_id] if mode_id in GAME_MODE else '未知'

	lobby_id = match['lobby_type']
	lobby = LOBBY[lobby_id] if lobby_id in LOBBY else '未知'
	scores = [match['radiant_score'], match['dire_score']]
	player_num = len(player_list)
	solo = 1 if player_num == 1 else 0
    # 更新玩家对象的比赛信息
	for i in player_list:
		for j in match['players']:
			if i.short_steamID == j['account_id']:
				i.dota2_kill = j['kills']
				i.dota2_death = j['deaths']
				i.dota2_assist = j['assists']
				i.kda = ((1. * i.dota2_kill + i.dota2_assist) / i.dota2_death) if i.dota2_death != 0 else (1. * i.dota2_kill + i.dota2_assist)
				i.dota2_team = get_team_by_slot(j['player_slot'])
				i.hero = int(j['hero_id'])
				i.last_hit = j['last_hits']
				i.damage = j['hero_damage']
				i.gpm = j['gold_per_min']
				i.xpm = j['xp_per_min']
				break
    # 队伍信息
	team = player_list[0].dota2_team
	if team == 2:
		scores.reverse()
	team_damage = 0
	team_kills = 0
	team_deaths = 0
	for i in match['players']:
		if get_team_by_slot(i['player_slot']) == team:
			team_damage += i['hero_damage']
			team_kills += i['kills']
			team_deaths += i['deaths']

	win = 0
	if match['radiant_win'] and team == 1:
		win = 1
	elif not match['radiant_win'] and team == 2:
		win = 1
	elif match['radiant_win'] and team == 2:
		win = 0
	elif not match['radiant_win'] and team == 1:
		win = 0

	print_str = ""
	if solo:
		print_str = player_list[0].nickname
	else:
		for i in range(player_num - 1):
			print_str += player_list[i].nickname+', '
		print_str += "和"+player_list[player_num-1].nickname

	top_kda = 0
	for i in player_list:
		if i.kda > top_kda:
			top_kda = i.kda

	if (win and top_kda > 10) or (not win and top_kda > 6):
		postive = 1
	elif (win and top_kda < 4) or (not win and top_kda < 1):
		postive = 0
	else:
		postive = random.randint(0, 1)

	print_str = random.choice(Messages[solo*4+win*2+postive]).format(print_str)

	start_time = datetime.datetime.fromtimestamp(match['start_time'], tz=pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
	duration = match['duration']
	print_str += "\n开始时间: {}".format(start_time)
	print_str += "\n持续时间: {:.0f}:{:.0f}".format(
		duration / 60, duration % 60)
	print_str += "\n游戏模式: [{}/{}]".format(mode, lobby)
	print_str += "\n总比分： {}:{}".format(scores[0], scores[1])
	print_str += "\n战绩详情: https://zh.dotabuff.com/matches/{}".format(match_id)
	# m = [print_str]
	for i in player_list:
		hero = HEROES_LIST_CHINESE[i.hero] if i.hero in HEROES_LIST_CHINESE else '不知道什么鬼'
		kda = i.kda
		last_hits = i.last_hit
		damage = i.damage
		kills, deaths, assists = i.dota2_kill, i.dota2_death, i.dota2_assist
		gpm, xpm = i.gpm, i.xpm

		damage_rate = 0 if team_damage == 0 else (100 * (float(damage) / team_damage))
		participation = 0 if team_kills == 0 else (100 * float(kills + assists) / team_kills)
		deaths_rate = 0 if team_deaths == 0 else (100 * float(deaths) / team_deaths)
		print_str += "\n\n{}使用{}\nKDA: {:.2f}[{}/{}/{}]\nGPM/XPM: {}/{}\n补刀数: {}\n总伤害: {}({:.2f}%)\n参战率: {:.2f}%\n参葬率: {:.2f}%" \
			.format(i.nickname, hero, kda, kills, deaths, assists, gpm, xpm, last_hits, damage, damage_rate, participation, deaths_rate)
		# m.append(print_str)
	return [print_str]
