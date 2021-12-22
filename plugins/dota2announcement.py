from pytz import timezone
import pytz
import requests
import re
from model.command import Command
from model.message_sender import GroupSender
from model.plugin import Plugin
from apscheduler.schedulers.background import BackgroundScheduler
from model.logger import logger


def parse(text: str) -> str:
    text = re.sub(r"\[img\].*\[/img\]", "", text)
    new_text = re.sub(r"\[([^\]]*)[^\]]*\]((.|\n)*?)\[\/\1\]", r"\2", text)
    while new_text != text:
        text = new_text
        new_text = re.sub(r"\[([^\]]*)[^\]]*\]((.|\n)*?)\[\/\1\]", r"\2", text)
    return text


class Announcement:
    def __init__(self, data: dict = {}) -> None:
        try:
            self.gid: int = data["gid"]
            self.title: str = data["headline"]
            self.content: str = parse(data["body"])
            self.update_time: int = data["updatetime"]
        except:
            self.gid = 0
            self.title = ""
            self.content = ""
            self.update_time = 0

    def __str__(self) -> str:
        return f"{self.title}\n\n{self.content}"


# EMPTY_ANNOUNCEMENT = Announcement({"gid": 0})


def get_announcements(count: int, offset: int = 0) -> list[Announcement]:
    logger.debug("Getting announcements...")
    url = "https://store.steampowered.com/events/ajaxgetpartnereventspageable/?appid=570&offset={}&count={}&l=schinese".format(
        offset, count)
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        j = resp.json()["events"]
        announcements: list[Announcement] = []
        for item in j:
            announcements.append(Announcement(item["announcement_body"]))
        if len(announcements) == 0:
            return [Announcement()]
        return announcements
    except requests.RequestException:
        return [Announcement()]


class Dota2Announcement(Plugin):
    __name = "DOTA2公告"

    def __init__(self, group_id: int, sender: GroupSender):
        super().__init__(group_id, sender)
        self._announcement = get_announcements(1)[0]
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.update, "interval", seconds=60, timezone=pytz.timezone('Asia/Shanghai'))
        self.scheduler.start()
        self.commands.append(
            Command(["查看公告"], [int], "index: 查看指定序号的公告", self.show_announcement))
        self.commands.append(
            Command(["公告列表"], [int], "index: 查看指定页数的公告列表", self.show_announcement_list))

    @classmethod
    def get_name(cls) -> str:
        return cls.__name

    def update(self):
        logger.debug("update announcement")
        announcement = get_announcements(1)[0]
        if announcement.gid == 0:
            return
        if self._announcement.gid != announcement.gid:
            self._announcement = announcement
            self.sender.send(str(self._announcement))
        elif self._announcement.update_time != announcement.update_time:
            self._announcement = announcement
            self.sender.send(str(self._announcement))
        else:
            pass

    def show_announcement(self, index: int, FromUserId: int):
        announcement = get_announcements(1, index-1)[0]
        if announcement.gid == 0:
            self.sender.send("找不到该公告")
            return
        self.sender.send(str(announcement))

    def show_announcement_list(self, page: int, FromUserId: int):
        offset = (page - 1) * 10
        announcements = get_announcements(10, offset)
        if announcements[0].gid == 0:
            self.sender.send("请输入正确的公告分页")
            return
        msg = "公告列表："
        for i, item in enumerate(announcements):
            msg += "\n{}. {}".format(offset + i + 1, item.title)
        self.sender.send(msg)
        return

    def shutdown(self):
        self.scheduler.shutdown()
        super().shutdown()
