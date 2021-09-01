class Account:
    # 基本属性
	short_steamID : int = 0
	long_steamID : int = 0
	qqid : int = 0
	nickname : str = ''
	last_DOTA2_match_ID : int = 0

	def __init__(self, nickname: str = "", qqid: int = 0, short_steamID: int = 0, long_steamID: int = 0, last_DOTA2_match_ID: int = 0):
		self.nickname = nickname
		self.qqid = qqid
		self.short_steamID = short_steamID
		self.long_steamID = long_steamID
		self.last_DOTA2_match_ID = last_DOTA2_match_ID