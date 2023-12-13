# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import config
from common import Httpx
from common.exceptions import FailedException

tools = {
    "url": "https://app.c.nf.migu.cn/MIGUM2.0/strategy/listen-url/v2.4?toneFlag=__quality__&songId=__songId__&resourceType=2",
    "qualityMap": {
        "128k": "PQ",
        "320k": "HQ",
        "flac": "SQ",
        "flac24bit": "ZQ",
    },
    "qualityMapReverse": {
        "PQ": "128k",
        "HQ": "320k",
        "SQ": "flac",
        "ZQ": "flac24bit",
    },
    "token": config.read_config("module.mg.user.token"),
    "aversionid": config.read_config("module.mg.user.aversionid"),
    "useragent": config.read_config("module.mg.user.useragent"),
    "osversion": config.read_config("module.mg.user.osversion"),
}


async def url(songId, quality):
    req = Httpx.request(
        tools["url"]
        .replace("__quality__", tools["qualityMap"][quality])
        .replace("__songId__", songId),
        {
            "method": "GET",
            "headers": {
                "User-Agent": tools["useragent"],
                "aversionid": tools["aversionid"],
                "token": tools["token"],
                "channel": "0146832",
                "language": "Chinese",
                "ua": "Android_migu",
                "mode": "android",
                "os": "Android " + tools["osversion"],
            },
        },
    )
    try:
        body = req.json()
        data = body["data"]

        if (not int(body["code"]) == 0) or (not data["url"]):
            raise FailedException("failed")

        return {
            "url": data["url"].split("?")[0],
            "quality": tools["qualityMapReverse"][data["audioFormatType"]],
        }
    except:
        raise FailedException("failed")
