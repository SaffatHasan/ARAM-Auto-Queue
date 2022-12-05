""" config.py
"""

# pylint: disable=C0103, R0903
from dataclasses import dataclass
from dataclass_wizard import YAMLWizard
from constants import QueueType, Roles


@dataclass
class Config(YAMLWizard, key_transform='SNAKE'):
    QUEUE_ID: QueueType
    PRIMARY_ROLE: Roles
    SECONDARY_ROLE: Roles

    @staticmethod
    def load():
        try:
            return Config.from_yaml_file('config.yaml')
        except (FileNotFoundError, ValueError, TypeError):
            return Config.default()

    @staticmethod
    def default():
        """ Returns an instance of Config with default values """
        return Config(
            QUEUE_ID=QueueType.RANKED,
            PRIMARY_ROLE=Roles.MID,
            SECONDARY_ROLE=Roles.JG,
        )

    def save(self):
        try:
            self.to_yaml_file('config.yaml')
        except PermissionError:
            return
