""" https://github.com/elliejs/Willump/blob/main/willump/proc_utils.py """

import time
import subprocess
from psutil import process_iter


def get_league_cmdline_args():
    return parse_cmdline_args(get_or_start_league_process())


def parse_cmdline_args(process):
    cmdline_args = process.cmdline()
    cmdline_args_parsed = {}
    for cmdline_arg in cmdline_args:
        if len(cmdline_arg) > 0 and '=' in cmdline_arg:
            key, value = cmdline_arg[2:].split('=')
            cmdline_args_parsed[key] = value
    return cmdline_args_parsed


def get_or_start_league_process():
    process = get_league_process()
    if not process:
        start_league()
        # Wait 5s for league client to start.
        time.sleep(5)
        league_process = get_league_process()

    if not league_process:
        raise FileNotFoundError
    return league_process


def get_league_process():
    for process in process_iter():
        if process.name() in ['LeagueClientUx.exe', 'LeagueClientUx']:
            return process
    return None


def start_league():
    # Start league client.
    league_path = 'C:\\Riot Games\\League of Legends\\LeagueClient.exe'
    subprocess.call([league_path])
