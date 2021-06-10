from typing import Union
from .logger import logger

import requests

from .account import Account
from .error import DOTA2HTTPError


def is_radiant(slot: int) -> bool:
    if slot < 128:
        return True
    else:
        return False


class MatchPlayer:
    account : Union[Account, None]
    persona : str
    account_id : int
    kills : int
    deaths : int
    assists : int
    radiant : bool
    kda : float
    gpm : int
    xpm : int
    hero : int
    last_hits : int
    denies : int
    damage : int

    def __init__(self, data: dict) -> None:
        self.persona = data['persona']
        self.account_id = data['account_id']
        self.radiant = is_radiant(data['player_slot'])
        self.hero = data['hero_id']
        
        self.kills = data['kills']
        self.deaths = data['deaths']
        self.assists = data['assists']
        self.kda = (1. * self.kills + self.assists) / (1 if self.deaths == 0 else self.deaths)
        
        self.gpm = data['gold_per_min']
        self.xpm = data['xp_per_min']
        
        self.last_hits = data['last_hits']
        self.denies = data['denies']
        
        self.damage = data['hero_damage']
        self.account = None


class Match:
    match_id : int
    radiant_win : bool
    players : list[MatchPlayer]
    mode : int
    typ : int
    scores : list[int]
    duration : int
    start_time : int
    def __init__(self, data: dict) -> None:
        logger.debug('match detail init')
        self.match_id = data['match_id']
        self.duration = data['duration']
        self.start_time = data['start_time']
        self.radiant_win = data['radiant_win']
        self.mode = data['game_mode']
        self.typ = data['lobby_type']
        self.scores = [data['radiant_score'], data['dire_score']]
        self.players = []
        for p in data['players']:
            self.players.append(MatchPlayer(p))
            
def get_match_detail(match_id: int, api_key: str) -> Match:
    url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1' \
          '?key={}&match_id={}&include_persona_names=1'.format(api_key, match_id)
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
    logger.debug('match detail')
    return Match(match_info)
