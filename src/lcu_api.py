""" lcu_api.py

Wrapper for league client API
"""

from json import dumps
from urllib.parse import urljoin
import time
from requests import Session
from urllib3 import disable_warnings, exceptions
from proc_utils import get_league_cmdline_args
from config import Config
from constants import queue_has_roles


class LeagueAPI:
    def __init__(self, config: Config):
        self.config = config
        self.sleep_duration = 1
        process_args = get_league_cmdline_args()
        self.base_url = f'https://127.0.0.1:{process_args["app-port"]}/'
        self.__session = Session()
        self.__session.auth = ('riot', process_args['remoting-auth-token'])
        self.__session.verify = False  # LCU api uses a self-signed cert
        disable_warnings(exceptions.InsecureRequestWarning)

    def loop(self):
        while True:
            self.run()
            time.sleep(self.sleep_duration)

    def run(self):
        # pylint: disable=R0912
        phase = self.session_phase()
        if phase is None:
            if not self.config.AUTO_LOBBY:
                return
            self.create_lobby()
            self.select_roles()
        elif phase == 'Lobby':
            if self.is_lobby_leader() and self.lobby_queue_id() != self.config.QUEUE_ID.value:
                self.create_lobby()
            if self.is_waiting_on_dodge_timer():
                return
            self.select_roles()
            self.queue()
        elif phase == 'Matchmaking':
            pass
        elif phase == 'ReadyCheck':
            self.accept()
        elif phase in ['ChampSelect', 'InProgress']:
            # ChampSelect and InProgress are long-lived.
            time.sleep(self.sleep_duration)
        elif phase == 'PreEndOfGame':
            self.level_change_ack()
            self.reward_granted_ack()
            self.mutual_honor_ack()
            self.honor_player()
        elif phase == 'EndOfGame':
            self.play_again()

    def is_waiting_on_dodge_timer(self):
        dodge_ids = self.request(
            'get', '/lol-gameflow/v1/session').json()['gameDodge']['dodgeIds']

        return len(dodge_ids) > 0

    def select_roles(self):
        if not queue_has_roles(self.config.QUEUE_ID):
            return
        self.select_position_preferences()

    def update_config(self, config: Config):
        self.config = config
        config.save()

    def request(self, method: str, endpoint: str, data=None):
        return self.__session.request(method, urljoin(
            self.base_url, endpoint), data=dumps(data))

    def session_phase(self):
        return self.request(
            'get', '/lol-gameflow/v1/session').json().get('phase')

    def is_lobby_leader(self):
        return self.request(
            'get',
            '/lol-gameflow/v1/gameflow-metadata/player-status',
        ).json()['currentLobbyStatus']['isLeader']

    def lobby_queue_id(self):
        current_queue_id = self.request(
            'get', '/lol-gameflow/v1/session').json()['gameData']['queue']['id']
        return current_queue_id

    def create_lobby(self):
        self.request('post', '/lol-lobby/v2/lobby',
                     {"queueId": self.config.QUEUE_ID.value})

    def queue(self):
        self.request('post', '/lol-lobby/v2/lobby/matchmaking/search')

    def stop_queue(self):
        self.request('delete', '/lol-lobby/v2/lobby/matchmaking/search')

    def select_position_preferences(self):
        return self.request(
            'put',
            '/lol-lobby/v2/lobby/members/localMember/position-preferences',
            {
                'firstPreference': self.config.PRIMARY_ROLE.value,
                'secondPreference': self.config.SECONDARY_ROLE.value,
            },
        )

    def accept(self):
        self.request('post', '/lol-matchmaking/v1/ready-check/accept')

    def honor_player(self, player_id=1):
        self.request('post', '/lol-honor-v2/v1/honor-player',
                     {'honorPlayerRequest': player_id})

    def level_change_ack(self):
        self.request('post', '/lol-honor-v2/v1/level-change/ack')

    def reward_granted_ack(self):
        self.request('post', '/lol-honor-v2/v1/reward-granted/ack')

    def mutual_honor_ack(self):
        self.request('post', '/lol-honor-v2/v1/mutual-honor/ack')

    def play_again(self):
        self.request('post', '/lol-lobby/v2/play-again')
