import requests
from typing import List

from model.beat_mods_version import BeatModsVersion
from model.mod import FileHash, Mod
from util.constants import *


def get_mods_for_version(version: BeatModsVersion) -> List[Mod]:
    """
    Gets available mods for a given version
    :param version: The version
    :return: A list of mods for that version
    """
    params = {
        "gameVersion": version.version,
        "status": "approved"
    }

    response = requests.get(BEAT_MODS_API + "mod", params=params)
    # comprehension is just too gross here.
    mods_list = []
    for mod in response.json():
        name = mod["name"]
        version = mod["version"]
        link = mod.get("link", None)
        files = [[FileHash(obj["file"], obj["hash"]) for obj in download["hashMd5"]] for download in mod["downloads"]]
        mods_list.append(Mod(name, version, link, files))

    return mods_list

