# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: variable.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

import os
import ujson as json


def _read_config_file():
    try:
        with open("./config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        pass


def _read_config(key):
    try:
        config = _read_config_file()
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                if k not in value and keys.index(k) != len(keys) - 1:
                    value[k] = {}
                elif k not in value and keys.index(k) == len(keys) - 1:
                    value = None
                value = value[k]
            else:
                value = None
                break

        return value
    except:
        return None


debug_mode = debug_mode if (debug_mode := _read_config("common.debug_mode")) else False
log_length_limit = (
    log_length_limit
    if (log_length_limit := _read_config("common.log_length_limit"))
    else 500
)
running = True
config = {}
default_config = None
workdir = os.getcwd()
banList_suggest = 0
iscn = True
fake_ip = None
