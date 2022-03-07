from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import Config
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from model.account import Account
from model.command import Command
from model.logger import logger
from model.match import get_match_detail
from model.message_sender import GroupSender
from model.plugin import Plugin

from .DotaDB import DotaDB as DB
from .utils import (generate_message, get_last_match_id_by_short_steamID,
                    steam_id_convert_32_to_64)


class Watcher(Plugin):
    """
    Dota2战绩自动查询插件
    """

    __name = "DOTA2战绩播报"

    def __init__(self, group_id: int, sender: GroupSender):
        super().__init__(group_id, sender)
        self.db = DB(group_id)
        self.result: dict[int, list[Account]] = {}
        self.pool = ThreadPoolExecutor(20)
        self.lock = Lock()
        self.accounts: list[Account] = self.db.get_accounts()
        logger.debug(self.accounts)
        for account in self.accounts:
            account = self.update_account(account)
        self.running = True
        # self.pool.submit(self.update)
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.update_once, 'interval', seconds=300, timezone=pytz.timezone('Asia/Shanghai'))
        self.scheduler.start()
        self.commands.append(
            Command(['查看监视'], [], '： 查看监视列表', self.show_watch))
        self.commands.append(
            Command(['添加监视'], [str, int, int], '昵称 Steam账号 QQ号： 添加新的监视账号', self.add_watch))
        self.commands.append(
            Command(['移除监视'], [int], '序号： 移除指定的监视账号', self.remove_watch))
        self.commands.append(
            Command(['更新分数'], [int, int], "序号 分数： 更新指定账号分数", self.update_score))
        self.commands.append(
            Command(['查看分数'], [int], "序号：查看指定账号分数", self.show_score))
        logger.debug('Dota2 Watcher({}) initialized.'.format(group_id))

    @classmethod
    def get_name(cls):
        return cls.__name

    def update_account(self, account: Account) -> Account:
        logger.debug('Watcher update account')
        try:
            match_id = get_last_match_id_by_short_steamID(
                account.short_steamID)
        except Exception as e:
            logger.error(repr(e))
            return account
        if match_id == -1:
            return account
        if match_id != account.last_DOTA2_match_ID:
            self.lock.acquire()
            if self.result.get(match_id, 0) != 0:
                self.result[match_id].append(account)
            else:
                self.result.update({match_id: [account]})
            self.lock.release()
            account.last_DOTA2_match_ID = match_id
            self.db.update_info(account)
        logger.debug('account update finish')
        return account

    def update_once(self):
        self.result.clear()
        if len(self.accounts) == 0:
            return
        if self.On():
            logger.debug('update watch')
            tmpList = self.pool.map(self.update_account, self.accounts)
            self.accounts = list(tmpList)
            logger.debug(self.result)
            for match_id in self.result:
                try:
                    match = get_match_detail(match_id, Config.stratz)
                except Exception as e:
                    logger.error('Get match detail error: {}'.format(e))
                    self.sender.send('获取战绩详情失败！')
                    continue
                for message in generate_message(match, self.result[match_id]):
                    self.sender.send(message)

                for player in match.players:
                    for i, account in enumerate(self.accounts):
                        if player.account_id == account.short_steamID:
                            score = account.score + player.score_change
                            if score < 10:
                                score = 10
                            account.score = score
                            self.accounts[i] = account
                            self.db.update_info(account)

    def shutdown(self):
        self.running = False
        self.scheduler.shutdown()
        self.pool.shutdown()
        super().shutdown()

    def add_watch(self, nickname: str, shortID: int, qqid: int, score: int, user: int):
        if self.db.is_account_stored(shortID):
            logger.warning('Player already watched.')
            self.sender.send('该账号已经存在，请勿重复添加！')
            return
        longID = steam_id_convert_32_to_64(shortID)
        last_match = get_last_match_id_by_short_steamID(shortID)
        account = Account(nickname, qqid, shortID, longID, last_match, score)
        self.db.insert_info(account)
        self.accounts.append(account)
        logger.success('Player information added successfully.')
        self.sender.send('添加监视成功！')

    def remove_watch(self, index: int, user: int):
        try:
            shortID = self.accounts[index - 1].short_steamID
            if self.db.is_account_stored(shortID):
                self.db.delete_info(shortID)
            del self.accounts[index - 1]
        except Exception as e:
            logger.error('Remove Watch Error: {}'.format(repr(e)))
            self.sender.send('移除监视失败！')
        else:
            logger.success('Remove Watch Successfully!')
            self.sender.send('移除监视成功！')

    def show_watch(self, user: int):
        # print(self.accounts)
        if len(self.accounts) == 0:
            m = '没有正在监视的账号！'
            self.sender.send(m)
            return
        m = '以下账号被监视中：'
        for index, account in enumerate(self.accounts):
            m += '\n{}. {}({})'.format(index + 1,
                                       account.nickname, account.short_steamID)
        if len(m):
            self.sender.send(m)

    def update_score(self, index: int, score: int, user: int):
        try:
            account = self.accounts[index-1]
            account.score = score
            self.accounts[index-1] = account
            self.db.update_info(account)
        except Exception as e:
            logger.error("Update score error: {}".format(e))
            self.sender.send("更新分数失败！")
        else:
            logger.success("Update score succeed!")
            self.sender.send("更新分数成功！")

    def show_score(self, index: int, user: int):
        account = self.accounts[index-1]
        self.sender.send("{}目前分数为：{}".format(account.nickname, account.score))


def test():
    Config.Load('./config.json')
    DB.connect()
