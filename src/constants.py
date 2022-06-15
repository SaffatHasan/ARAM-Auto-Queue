""" constants.py

"""

from enum import Enum


class QueueType(Enum):
    """
        List of valid queue IDs are listed here:
        https://static.developer.riotgames.com/docs/lol/queues.json
    """
    ARAM = 450
    ARURF = 900
    DRAFT = 400
    RANKED = 420
    BLIND = 430
    FLEX = 440


def queue_has_roles(queue: QueueType):
    return queue in [
        QueueType.DRAFT,
        QueueType.FLEX,
        QueueType.RANKED
    ]


class Roles(Enum):
    TOP = "TOP"
    JG = "JUNGLE"
    MID = "MIDDLE"
    BOT = "BOTTOM"
    SUPP = "SUPPORT"
    FILL = "FILL"