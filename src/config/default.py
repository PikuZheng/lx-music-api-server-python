import os
import yaml
from common import variable
from .log import logger


def handleReadDefaultConfig():
    defaultFilePath = os.path.abspath(
        os.path.dirname(os.path.abspath(__file__)) + "./default.yaml"
    )
    config = None

    with open(defaultFilePath, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

    return config


def handleWriteDefaultConfig(path="./config.yaml"):
    defaultFilePath = os.path.abspath(
        os.path.dirname(os.path.abspath(__file__)) + "./default.yaml"
    )
    defaultConfig = None

    with open(defaultFilePath, "r", encoding="utf-8") as f:
        defaultConfig = f.read()
        f.close()

    with open(path, "w", encoding="utf-8") as f:
        f.write(defaultConfig)
        f.close()

    if not os.getenv("build"):
        logger.info("首次启动或配置文件被删除，已创建默认配置文件")
        logger.info(f"\n建议您到{variable.workdir + os.path.sep}config.yaml修改配置后重新启动服务器")


def handleGetDefaultConfig(key):
    try:
        keys = key.split(".")
        value = variable.default_config
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
        logger.warning(f"配置文件{key}不存在")
        return None


def handleInitDefaultConfig():
    config = handleReadDefaultConfig()

    variable.default_config = config
