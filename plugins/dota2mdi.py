import Config
from model.command import Command
from model.message_sender import GroupSender
from model.plugin import Plugin
import requests, base64

class Mdi(Plugin):
    __name = "DOTA2战绩图"
    def __init__(self, group_id: int, sender: GroupSender):
        super().__init__(group_id, sender)
        self.commands.append(
            Command(['战绩图'], [int], 'match_id： 显示Dota2战绩图', self.get_image))

    def get_image(self, match_id: int, FromUserId: int) -> None:
        url = Config.mdi_url+"/match?id="+str(match_id)
        self.sender.send('战绩图正在生成中...')
        r = requests.get(url)
        data = base64.b64encode(r.content)
        self.sender.send_image_by_base64(str(data, encoding="utf-8"), '战绩图生成成功！')

    @classmethod
    def get_name(cls):
        return cls.__name
