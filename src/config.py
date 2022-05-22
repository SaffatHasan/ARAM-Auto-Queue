""" config.py
"""

# pylint: disable=C0103, R0903
import yaml
from constants import QueueType, Roles


class Config:
    def __init__(self):
        try:
            with open('config.yaml', 'r', encoding='utf8') as f:
                saved_data = yaml.load(f, Loader=yaml.Loader)
                self.AUTO_LOBBY = saved_data['auto_lobby']
                self.QUEUE_ID = saved_data['queue_type']
                self.AUTO_QUEUE = saved_data['auto_queue']
                self.AUTO_ACCEPT = saved_data['auto_accept']
                self.AUTO_SKIP_POSTGAME = saved_data['auto_skip_postgame']
                self.AUTO_PLAY_AGAIN = saved_data['auto_play_again']
                self.PRIMARY_ROLE = saved_data['primary_role']
                self.SECONDARY_ROLE = saved_data['secondary_role']
        except FileNotFoundError:
            self.default()

    def default(self):
        self.AUTO_LOBBY = True
        self.QUEUE_ID = QueueType.RANKED
        self.AUTO_QUEUE = True
        self.AUTO_ACCEPT = True
        self.AUTO_SKIP_POSTGAME = True
        self.AUTO_PLAY_AGAIN = True
        self.PRIMARY_ROLE = Roles.MID
        self.SECONDARY_ROLE = Roles.JG

    def save(self):
        try:
            with open('config.yaml', 'w', encoding='utf8') as f:
                data = {
                    'auto_lobby': self.AUTO_LOBBY,
                    'queue_type': self.QUEUE_ID,
                    'auto_queue': self.AUTO_QUEUE,
                    'auto_accept': self.AUTO_ACCEPT,
                    'auto_skip_postgame': self.AUTO_SKIP_POSTGAME,
                    'auto_play_again': self.AUTO_PLAY_AGAIN,
                    'primary_role': self.PRIMARY_ROLE,
                    'secondary_role': self.SECONDARY_ROLE,
                }

                yaml.dump(data, f)
        except PermissionError:
            return
