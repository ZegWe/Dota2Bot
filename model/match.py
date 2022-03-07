from time import sleep
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
    account: Account
    persona: str
    account_id: int
    kills: int
    deaths: int
    assists: int
    radiant: bool
    kda: float
    gpm: int
    xpm: int
    hero: int
    last_hits: int
    denies: int
    damage: int
    party_size: int
    party_id: int
    leaver: int
    score_change: int

    def __init__(self, data: dict) -> None:
        self.persona = data['steamAccount']['name']
        self.account_id = data['steamAccount']['id']
        self.radiant = data['isRadiant']
        self.hero = data['heroId']

        self.kills = data['numKills']
        self.deaths = data['numDeaths']
        self.assists = data['numAssists']
        self.kda = (1. * self.kills + self.assists) / \
            (1 if self.deaths == 0 else self.deaths)

        self.gpm = data['goldPerMinute']
        self.xpm = data['experiencePerMinute']

        self.last_hits = data['numLastHits']
        self.denies = data['numDenies']

        self.damage = data['heroDamage']

        self.party_id = data.get('partyId', -1)
        self.leaver = data['leaverStatus']

        self.account = Account()


class Match:
    match_id: int
    radiant_win: bool
    players: list[MatchPlayer]
    mode: int
    typ: int
    scores: list[int]
    duration: int
    start_time: int

    def __init__(self, data: dict) -> None:
        logger.debug('match detail init')
        self.match_id = data['id']
        self.duration = data['durationSeconds']
        self.start_time = data['startDateTime']
        self.radiant_win = data['didRadiantWin']
        self.mode = data['gameMode']
        self.typ = data['lobbyType']
        self.scores = [0, 0]
        self.players = []
        for p in data['players']:
            self.players.append(MatchPlayer(p))
        tmp: dict[int, int] = {}
        for p in self.players:
            if p.radiant:
                self.scores[0] += p.kills
            else:
                self.scores[1] += p.kills
            tmp[p.party_id] += 1 if p.party_id != -1 else 0

        for i, p in enumerate(self.players):
            p.party_size = tmp[p.party_id]
            p.score_change = (20 if p.party_size > 1 else 30) * \
                (1 if p.leaver == 0 and (p.radiant == self.radiant_win) else -1)
            self.players[i] = p


def get_match_detail(match_id: int, token: str) -> Match:
    url = 'https://api.stratz.com/api/v1/match/{}?jwt={}'.format(
        match_id, token)
    for _ in range(0,4):
        try:
            response = requests.get(url)
        except requests.RequestException:
            raise DOTA2HTTPError("Requests Error.")
        if response.status_code != 200:
            if response.status_code == 204:
                logger.warning("Get match detail failed, retrying...\n{}".format(response))
                sleep(60)
                continue
            raise DOTA2HTTPError(
                "Failed to retrieve data: %s. URL: %s" % (response.status_code, url))
        match = response.json()
        return Match(match)
    
    raise DOTA2HTTPError("Failed for too many times")
