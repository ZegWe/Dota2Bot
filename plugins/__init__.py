from .dota2fortune import Fortune
from .dota2mdi import Mdi
from .dota2watcher import Dota2Watcher

plugin_list: list = [
    Fortune,
    Dota2Watcher,
    Mdi
]

PLUGIN_DICT: dict = {}

for plugin in plugin_list:
    PLUGIN_DICT[plugin.get_name()] = plugin