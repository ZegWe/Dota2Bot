class Player:
    # 基本属性
	short_steamID : int = 0
	long_steamID : int = 0
	qqid : int = 0
	nickname : str = ''
	last_DOTA2_match_ID : int = 0

    # 玩家在最新的一场比赛中的数据
    # dota2专属
	dota2_kill : int = 0
	dota2_death : int = 0
	dota2_assist : int = 0
    # 1为天辉, 2为夜魇
	dota2_team : int = 1
	kda : float = 0
	gpm : int = 0
	xpm : int = 0
	hero : int = 0
	last_hit : int = 0
	damage : int = 0

	def __init__(self, nickname: str, qqid: int, short_steamID: int, long_steamID: int, last_DOTA2_match_ID: int):
		self.nickname = nickname
		self.qqid = qqid
		self.short_steamID = short_steamID
		self.long_steamID = long_steamID
		self.last_DOTA2_match_ID = last_DOTA2_match_ID