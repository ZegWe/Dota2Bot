from .dota2fortune import Fortune
from .dota2watcher import Dota2Watcher

PLUGIN_DICT : dict = {
	Dota2Watcher.get_name() : Dota2Watcher,
	Fortune.get_name() : Fortune
}
