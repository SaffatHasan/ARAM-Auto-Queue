""" https://github.com/elliejs/Willump/blob/main/willump/proc_utils.py """

import time
from psutil import process_iter


def lcu_process_args():
    return parse_cmdline_args(find_lcu_process().cmdline())


def parse_cmdline_args(cmdline_args):
    cmdline_args_parsed = {}
    for cmdline_arg in cmdline_args:
        if len(cmdline_arg) > 0 and '=' in cmdline_arg:
            key, value = cmdline_arg[2:].split('=')
            cmdline_args_parsed[key] = value
    return cmdline_args_parsed


def find_lcu_process():
    max_tries = 5
    for _ in range(max_tries):
        for process in process_iter():
            if process.name() in ['LeagueClientUx.exe', 'LeagueClientUx']:
                return process
        time.sleep(0.1)
    raise FileNotFoundError
