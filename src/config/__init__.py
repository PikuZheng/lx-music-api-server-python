# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: config.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

import ujson as json
import time
import os
import traceback
import sqlite3
import yaml
import threading
from common import variable
from .log import logger
from . import default


# 创建线程本地存储对象
local_data = threading.local()


def get_data_connection():
    # 检查线程本地存储对象是否存在连接对象，如果不存在则创建一个新的连接对象
    if not hasattr(local_data, "connection"):
        local_data.connection = sqlite3.connect("data.db")
    return local_data.connection


# 创建线程本地存储对象
local_cache = threading.local()


def get_cache_connection():
    # 检查线程本地存储对象是否存在连接对象，如果不存在则创建一个新的连接对象
    if not hasattr(local_cache, "connection"):
        local_cache.connection = sqlite3.connect("cache.db")
    return local_cache.connection


class ConfigReadException(Exception):
    pass


def handleReadConfig():
    configFilePath = "./config.yaml"
    config = {}

    if not os.path.exists(configFilePath):
        default.handleWriteDefaultConfig(configFilePath)
        return variable.default_config

    with open(configFilePath, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

    return config


def handleInitConfig():
    config = handleReadConfig()

    variable.config = config


def load_data():
    config_data = {}
    try:
        # Connect to the database
        conn = get_data_connection()
        cursor = conn.cursor()

        # Retrieve all configuration data from the 'config' table
        cursor.execute("SELECT key, value FROM data")
        rows = cursor.fetchall()

        for row in rows:
            key, value = row
            config_data[key] = json.loads(value)

    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        logger.error(traceback.format_exc())

    return config_data


def save_data(config_data):
    try:
        # Connect to the database
        conn = get_data_connection()
        cursor = conn.cursor()

        # Clear existing data in the 'data' table
        cursor.execute("DELETE FROM data")

        # Insert the new configuration data into the 'data' table
        for key, value in config_data.items():
            cursor.execute(
                "INSERT INTO data (key, value) VALUES (?, ?)", (key, json.dumps(value))
            )

        conn.commit()

    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        logger.error(traceback.format_exc())


def getCache(module, key):
    try:
        # 连接到数据库（如果数据库不存在，则会自动创建）
        conn = get_cache_connection()

        # 创建一个游标对象
        cursor = conn.cursor()

        cursor.execute("SELECT data FROM cache WHERE module=? AND key=?", (module, key))

        result = cursor.fetchone()
        if result:
            cache_data = json.loads(result[0])
            if not cache_data["expire"]:
                return cache_data
            if int(time.time()) < cache_data["time"]:
                return cache_data
    except:
        pass
        # traceback.print_exc()
    return False


def updateCache(module, key, data):
    try:
        # 连接到数据库（如果数据库不存在，则会自动创建）
        conn = get_cache_connection()

        # 创建一个游标对象
        cursor = conn.cursor()

        cursor.execute("SELECT data FROM cache WHERE module=? AND key=?", (module, key))
        result = cursor.fetchone()
        if result:
            cache_data = json.loads(result[0])
            if isinstance(cache_data, dict):
                cache_data.update(data)
            else:
                logger.error(
                    f"Cache data for module '{module}' and key '{key}' is not a dictionary."
                )
        else:
            cursor.execute(
                "INSERT INTO cache (module, key, data) VALUES (?, ?, ?)",
                (module, key, json.dumps(data)),
            )

        conn.commit()
    except:
        logger.error("缓存写入遇到错误…")
        logger.error(traceback.format_exc())


def resetRequestTime(ip):
    config_data = load_data()
    try:
        try:
            config_data["requestTime"][ip] = 0
        except KeyError:
            config_data["requestTime"] = {}
            config_data["requestTime"][ip] = 0
        save_data(config_data)
    except:
        logger.error("配置写入遇到错误…")
        logger.error(traceback.format_exc())


def updateRequestTime(ip):
    try:
        config_data = load_data()
        try:
            config_data["requestTime"][ip] = time.time()
        except KeyError:
            config_data["requestTime"] = {}
            config_data["requestTime"][ip] = time.time()
        save_data(config_data)
    except:
        logger.error("配置写入遇到错误...")
        logger.error(traceback.format_exc())


def getRequestTime(ip):
    config_data = load_data()
    try:
        value = config_data["requestTime"][ip]
    except:
        value = 0
    return value


def read_data(key):
    config = load_data()
    keys = key.split(".")
    value = config
    for k in keys:
        if k not in value and keys.index(k) != len(keys) - 1:
            value[k] = {}
        elif k not in value and keys.index(k) == len(keys) - 1:
            value = None
        value = value[k]

    return value


def write_data(key, value):
    config = load_data()

    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value

    save_data(config)


def push_to_list(key, obj):
    config = load_data()

    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    if keys[-1] not in current:
        current[keys[-1]] = []

    current[keys[-1]].append(obj)

    save_data(config)


def write_config(key, value):
    config = handleReadConfig()

    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value
    variable.config = config

    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=None)
        f.close()


def _read_config(key):
    try:
        config = variable.config
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                if k not in value and keys.index(k) != len(keys) - 1:
                    value[k] = None
                elif k not in value and keys.index(k) == len(keys) - 1:
                    value = None
                value = value[k]
            else:
                value = None
                break

        return value
    except (KeyError, TypeError):
        return None


def read_config(key):
    try:
        config = variable.config
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
        default_value = default.handleGetDefaultConfig(key)
        if isinstance(default_value, type(None)):
            logger.warning(f"配置文件{key}不存在")
        else:
            for i in range(len(keys)):
                tk = ".".join(keys[: (i + 1)])
                tkvalue = _read_config(tk)
                logger.debug(f"configfix: 读取配置文件{tk}的值：{tkvalue}")
                if (tkvalue is None) or (tkvalue == {}):
                    write_config(tk, default.handleGetDefaultConfig(tk))
                    logger.info(f"配置文件{tk}不存在，已创建")
                    return default_value


def write_data(key, value):
    config = load_data()

    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value

    save_data(config)


def initConfig():
    handleInitConfig()

    variable.log_length_limit = read_config("common.log_length_limit")
    variable.debug_mode = read_config("common.debug_mode")
    logger.debug("配置文件加载成功")
    conn = sqlite3.connect("cache.db")

    # 创建一个游标对象
    cursor = conn.cursor()

    # 创建一个表来存储缓存数据
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS cache
(id INTEGER PRIMARY KEY AUTOINCREMENT,
module TEXT NOT NULL,
key TEXT NOT NULL,
data TEXT NOT NULL)"""
    )

    conn.close()

    conn2 = sqlite3.connect("data.db")

    # 创建一个游标对象
    cursor2 = conn2.cursor()

    cursor2.execute(
        """CREATE TABLE IF NOT EXISTS data
(key TEXT PRIMARY KEY,
value TEXT)"""
    )

    conn2.close()

    logger.debug("数据库初始化成功")

    # print
    if load_data() == {}:
        write_data("banList", [])
        write_data("requestTime", {})
        logger.info("数据库内容为空，已写入默认值")

    # 处理代理配置
    if read_config("common.proxy.enable"):
        if read_config("common.proxy.http_value"):
            os.environ["http_proxy"] = read_config("common.proxy.http_value")
            logger.info("HTTP协议代理地址: " + read_config("common.proxy.http_value"))
        if read_config("common.proxy.https_value"):
            os.environ["https_proxy"] = read_config("common.proxy.https_value")
            logger.info("HTTPS协议代理地址: " + read_config("common.proxy.https_value"))
        logger.info("代理功能已开启，请确保代理地址正确，否则无法连接网络")


def ban_ip(ip_addr, ban_time=-1):
    if read_config("security.banlist.enable"):
        banList = read_data("banList")
        banList.append(
            {
                "ip": ip_addr,
                "expire": read_config("security.banlist.expire.enable"),
                "expire_time": read_config("security.banlist.expire.length")
                if (ban_time == -1)
                else ban_time,
            }
        )
        write_data("banList", banList)
    else:
        if variable.banList_suggest < 10:
            variable.banList_suggest += 1
            logger.warning("黑名单功能已被关闭，我们墙裂建议你开启这个功能以防止恶意请求")


def check_ip_banned(ip_addr):
    if read_config("security.banlist.enable"):
        banList = read_data("banList")
        for ban in banList:
            if ban["ip"] == ip_addr:
                if ban["expire"]:
                    if ban["expire_time"] > int(time.time()):
                        return True
                    else:
                        banList.remove(ban)
                        write_data("banList", banList)
                        return False
                else:
                    return True
            else:
                return False
        return False
    else:
        if variable.banList_suggest <= 10:
            variable.banList_suggest += 1
            logger.warning("黑名单功能已被关闭，我们墙裂建议你开启这个功能以防止恶意请求")
        return False


default.handleInitDefaultConfig()
initConfig()
