
import json
import requests


GAME_MODE = {
    0: "No Game Mode",
    1: "全英雄选择",
    2: "队长模式",
    3: "随机征召",
    4: "小黑屋",
    5: "全部随机",
    7: "万圣节活动",
    8: "反队长模式",
    9: "贪魔活动",
    10: "教程",
    11: "中路模式",
    12: "生疏模式",
    13: "新手模式",
    14: "Compendium Matchmaking",
    15: "自定义游戏",
    16: "队长征召",
    17: "平衡征召",
    18: "OMG",
    19: "活动模式",
    20: "全英雄死亡随机",
    21: "中路SOLO",
    22: "全英雄选择",
    23: "加速模式"
}


LOBBY = {
    -1: "非法ID",
    0: "普通匹配",
    1: "练习",
    2: "锦标赛",
    3: "教程",
    4: "合作对抗电脑",
    5: "组排模式",
    6: "单排模式",
    7: "天梯匹配",
    8: "中路SOLO",
        12: "活动房间"
}


# 服务器ID列表
AREA_CODE = {
    111: "美国西部",
    112: "美国西部",
    114: "美国西部",
    121: "美国东部",
    122: "美国东部",
    123: "美国东部",
    124: "美国东部",
    131: "欧洲西部",
    132: "欧洲西部",
    133: "欧洲西部",
    134: "欧洲西部",
    135: "欧洲西部",
    136: "欧洲西部",
    142: "南韩",
    143: "南韩",
    151: "东南亚",
    152: "东南亚",
    153: "东南亚",
    161: "中国",
    163: "中国",
    171: "澳大利亚",
    181: "俄罗斯",
    182: "俄罗斯",
    183: "俄罗斯",
    184: "俄罗斯",
    185: "俄罗斯",
    186: "俄罗斯",
    191: "欧洲东部",
    192: "欧洲东部",
    200: "南美洲",
    202: "南美洲",
    203: "南美洲",
    204: "南美洲",
    211: "非洲南部",
    212: "非洲南部",
    213: "非洲南部",
    221: "中国",
    222: "中国",
    223: "中国",
    224: "中国",
    225: "中国",
    231: "中国",
    236: "中国",
    242: "智利",
    251: "秘鲁",
    261: "印度"}


class Hero():
    id: int
    name: str
    name_sc: str
    name_en: str
    img: str


HeroList: dict[int, Hero] = {}


CUSTOM_HERO_LIST: dict[str, str] = {}


def refresh_hero_list():
    global HeroList
    with requests.get("https://raw.githubusercontent.com/ZegWe/Dota2Data/main/data/hero.json") as resp:
        j = json.loads(resp.content)
        hero_list: dict[int, Hero] = {}
        for item in j['hero_list']:
            hero = Hero()
            hero.id = item['id']
            hero.name = item['name']
            hero.name_sc = item['name_sc']
            hero.name_en = item['name_en']
            hero.img = item['img']
            hero_list[hero.id] = hero

        for k, v in hero_list.items():
            if v.name_sc in CUSTOM_HERO_LIST:
                hero_list[k].name_sc = CUSTOM_HERO_LIST[v.name_sc]
        HeroList = hero_list


def get_hero_list() -> dict[int, Hero]:
    return HeroList
