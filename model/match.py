from re import T
from time import sleep
from .logger import logger

import requests
import Config

from .account import Account
from .error import DOTA2HTTPError
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


query = gql(
"""
query getMatch ($id: Long!){
    match(id: $id) {
        id
        durationSeconds
        startDateTime
        didRadiantWin
        gameMode
        lobbyType
        players {
            kills
            deaths
            assists
            isRadiant
            heroId
            goldPerMinute
            experiencePerMinute
            numLastHits
            numDenies
            heroDamage
            partyId
            leaverStatus
            steamAccount {
                id
                name
            }
        }
    }
}
"""
)

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
    leaver: bool
    score_change: int

    def __init__(self, data: dict) -> None:
        self.persona = data['steamAccount']['name']
        self.account_id = data['steamAccount']['id']
        self.radiant = data['isRadiant']
        self.hero = data['heroId']

        self.kills = data['kills']
        self.deaths = data['deaths']
        self.assists = data['assists']
        self.kda = (1. * self.kills + self.assists) / \
            (1 if self.deaths == 0 else self.deaths)

        self.gpm = data['goldPerMinute']
        self.xpm = data['experiencePerMinute']

        self.last_hits = data['numLastHits']
        self.denies = data['numDenies']

        self.damage = data['heroDamage']

        self.party_id = data.get('partyId', -1)
        if self.party_id == None:
            self.party_id = -1
        self.leaver = data['leaverStatus'] != "NONE"

        self.account = Account()


class Match:
    match_id: int
    radiant_win: bool
    players: list[MatchPlayer]
    mode: str
    typ: str
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
            t = tmp.get(p.party_id, 0)
            t += 1 if p.party_id != -1 else 0
            tmp[p.party_id] = t

        for i, p in enumerate(self.players):
            p.party_size = tmp[p.party_id]
            if self.typ == "RANKED":
                p.score_change = (20 if p.party_size > 1 else 30) * \
                    (1 if not p.leaver and (p.radiant == self.radiant_win) else -1)
            else:
                p.score_change = 0
            self.players[i] = p

def get_match_detail(id: int) -> Match:
    url = "https://api.stratz.com/graphql?jwt="+Config.stratz
    trans = RequestsHTTPTransport(url=url)
    client = Client(transport=trans)
    for i in range(0,3):
        sleep(60)
        try:
            data = client.execute(query, variable_values={'id': id})
            if data['match'] == None:
                logger.warning(
                    "Get match detail failed, retrying...{}\n{}".format(i+1, data))
                continue
            return Match(data['match'])
        except Exception as e:
            raise(e)
        
    raise DOTA2HTTPError("Failed for too many times\n{}".format(url))


def get_detail(match_id: int, token: str) -> Match:
    url = 'https://api.stratz.com/api/v1/match/{}?jwt={}'.format(
        match_id, token)
    for i in range(0, 3):
        sleep(60)
        try:
            logger.debug('getting match detail({})...'.format(i))
            response = requests.get(url)
        except requests.RequestException:
            raise DOTA2HTTPError("Requests Error.")
        if response.status_code != 200:
            if response.status_code == 204:
                logger.warning(
                    "Get match detail failed, retrying...{}\n{}".format(i+1, response))
                continue
            raise DOTA2HTTPError(
                "Failed to retrieve data: %s. URL: %s" % (response.status_code, url))
        match = response.json()
        # logger.debug(match)
        if match == None:
            continue
        return Match(match)

    raise DOTA2HTTPError("Failed for too many times\n{}".format(url))
