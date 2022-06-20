""" main.py

Entrypoint for AutoQr

"""

import multiprocessing
import sys
import os
import PySimpleGUI as sg
import urllib3
from config import Config
from constants import QueueType, Roles, queue_has_roles
from lcu_api import LeagueAPI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def launch_gui(league_api: LeagueAPI, cfg: Config):
    sg.theme('DefaultNoMoreNagging')
    layout = [
        [sg.Text(
            'Running',
            key='status',
            text_color='green',
        )],
        [sg.Text('Create lobby?', size=(16, 1)), sg.Checkbox(
            '',
            key='AUTO_LOBBY',
            default=cfg.AUTO_LOBBY,
            enable_events=True,
            expand_x=True,
            tooltip='Creates the game lobby for you (if you aren\'t already in one).',
        )],
        [sg.Text('Mode', size=(9, 1)), sg.Combo(
            [x.name for x in QueueType],
            key='QUEUE_ID',
            default_value=cfg.QUEUE_ID.name,
            disabled=not cfg.AUTO_LOBBY,
            readonly=True,
            enable_events=True,
            size=(8, 1),
        )],
        [sg.Text("Primary", size=(9, 1)), sg.Combo(
            [x.name for x in Roles],
            key='PRIMARY_ROLE',
            default_value=cfg.PRIMARY_ROLE.name,
            disabled=not queue_has_roles(cfg.QUEUE_ID),
            readonly=True,
            enable_events=True,
            size=(8, 1),
        )],
        [sg.Text("Secondary", size=(9, 1)), sg.Combo(
            [x.name for x in Roles],
            key='SECONDARY_ROLE',
            default_value=cfg.SECONDARY_ROLE.name,
            disabled=not queue_has_roles(cfg.QUEUE_ID),
            readonly=True,
            enable_events=True,
            size=(8, 1),
        )],
        [sg.Button('Stop', key='toggle')],
    ]
    window = sg.Window(
        title="AutoQr",
        layout=layout,
        icon=resource_path('favicon.ico'),
        finalize=True,
    )

    # Run lcu_api in the background, store its process in background_proc
    background_proc = update_state(
        league_api,
        window,
        background_proc=None,
        event='toggle',
        values=None)

    # GUI event loop handler
    while True:
        event, values = window.read()
        background_proc = update_state(
            league_api, window, background_proc, event, values)


def update_state(league_api, window, background_proc, event, values=None):
    """ Given the current event, transition to new state. E.g. if the user
    hits the start/stop button then we toggle behavior.
    """
    cfg = league_api.config
    if event == 'toggle':
        background_proc = toggle_process(background_proc, league_api)
        window['status'].update(
            'Running' if background_proc else 'Not running')
        window['status'].update(
            text_color='green' if background_proc else 'red')
        window['toggle'].update('Stop' if background_proc else 'Start')
        window['AUTO_LOBBY'].update(disabled=bool(background_proc))
        window['QUEUE_ID'].update(
            disabled=not cfg.AUTO_LOBBY or bool(background_proc))
        window['PRIMARY_ROLE'].update(
            disabled=not should_display_role_selection(cfg) or bool(background_proc))
        window['SECONDARY_ROLE'].update(
            disabled=not should_display_role_selection(cfg) or bool(background_proc))

    elif event == 'QUEUE_ID':
        cfg.QUEUE_ID = QueueType[values['QUEUE_ID']]
        window['PRIMARY_ROLE'].update(
            disabled=not should_display_role_selection(cfg) or bool(background_proc))
        window['SECONDARY_ROLE'].update(
            disabled=not should_display_role_selection(cfg) or bool(background_proc))

    # Checkboxes toggle the value
    elif event == 'AUTO_LOBBY':
        cfg.AUTO_LOBBY = not cfg.AUTO_LOBBY

        # Cannot select a queue ID if we are not creating a lobby anyways
        window['QUEUE_ID'].update(
            disabled=not cfg.AUTO_LOBBY or bool(background_proc))
        window['PRIMARY_ROLE'].update(
            disabled=not should_display_role_selection(cfg) or bool(background_proc))
        window['SECONDARY_ROLE'].update(
            disabled=not should_display_role_selection(cfg) or bool(background_proc))

    # TODO do not allow user to select the same role twice
    elif event == 'PRIMARY_ROLE':
        cfg.PRIMARY_ROLE = Roles[values['PRIMARY_ROLE']]

    elif event == 'SECONDARY_ROLE':
        cfg.SECONDARY_ROLE = Roles[values['SECONDARY_ROLE']]

    elif event == sg.WINDOW_CLOSED:
        if background_proc:
            league_api.stop_queue()
            background_proc.terminate()
        sys.exit(0)

    league_api.update_config(cfg)

    return background_proc


def should_display_role_selection(cfg: Config):
    if not cfg.AUTO_LOBBY:
        return False
    if not queue_has_roles(cfg.QUEUE_ID):
        return False
    return True


def toggle_process(proc, league_api):
    if proc is not None:
        league_api.stop_queue()
        proc.terminate()
        return None

    proc = multiprocessing.Process(target=league_api.loop, args=())
    proc.start()
    return proc


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller
    https://stackoverflow.com/a/13790741
    """
    # pylint: disable=W0703, W0212
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    config = Config.load()
    try:
        # TODO(saffathasan): WOW this is a huge code smell. Should config
        # really be embedded?
        launch_gui(LeagueAPI(config), config)
    except FileNotFoundError:
        sg.popup(
            'Failed to start',
            'Have you logged into League of Legends?',
            icon=resource_path('favicon.ico'),
            auto_close=True,
            auto_close_duration=5,
        )
