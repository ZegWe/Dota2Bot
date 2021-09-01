from model.db import BaseDB
from model.account import Account


class DotaDB(BaseDB):
    """
    基于BaseDB的Dota2战绩数据库，以供Dota2Watcher插件使用
    """
    __name = "Dota2 Player Info DB"
    def __init__(self, group_id: int):
        """
        :param group_id: Watcher提供的群号
        """
        self.group_id = group_id
        self.c.execute('''
		CREATE TABLE IF NOT EXISTS `playerInfo-{}`
		(short_steamID INT PRIMARYKEY NOT NULL,
		long_steamID INT NOT NULL,
		nickname CHAR(50) NOT NULL,
		qqid INT NOT NULL,
		last_DOTA2_match_ID INT);
		'''.format(group_id))
        self.conn.commit()

    @classmethod
    def get_name(cls) -> str:
        return cls.__name

    def get_accounts(self) -> list[Account]:
        """
        查询数据库中储存的所有玩家信息，返回一个player列表

        $return: 数据库中的player列表
        """
        accounts: list[Account] = []
        self.lock.acquire()
        cursor = self.c.execute(
            "SELECT * from `playerInfo-{}`".format(self.group_id))
        for row in cursor:
            account = Account(short_steamID=row[0],
                              long_steamID=row[1],
                              nickname=row[2],
                              qqid=row[3],
                              last_DOTA2_match_ID=row[4])
            accounts.append(account)
        self.lock.release()
        return accounts

    def update_DOTA2_match_ID(self, short_steamID, last_DOTA2_match_ID):
        self.lock.acquire()
        self.c.execute("UPDATE `playerInfo-{}` SET last_DOTA2_match_ID='{}' WHERE short_steamID={}"
                       .format(self.group_id, last_DOTA2_match_ID, short_steamID))
        self.conn.commit()
        self.lock.release()

    def insert_info(self, short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID):
        self.lock.acquire()
        self.c.execute("INSERT INTO `playerInfo-{}` (short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID) "
                       "VALUES ({}, {}, {}, '{}', '{}')"
                       .format(self.group_id, short_steamID, long_steamID, qqid, nickname, last_DOTA2_match_ID))
        self.conn.commit()
        self.lock.release()

    def delete_info(self, short_steamID):
        self.lock.acquire()
        self.c.execute(
            "DELETE FROM `playerInfo-{}` WHERE short_steamID={}".format(self.group_id, short_steamID))
        self.conn.commit()
        self.lock.release()

    def is_account_stored(self, short_steamID: int) -> bool:
        self.lock.acquire()
        self.c.execute(
            "SELECT * FROM `playerInfo-{}` WHERE short_steamID=={}".format(self.group_id, short_steamID))
        if len(self.c.fetchall()) == 0:
            self.lock.release()
            return False
        self.lock.release()
        return True
