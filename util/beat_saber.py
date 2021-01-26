import requests
import re
from pathlib import Path

from typing import Optional

from model.beat_mods_version import BeatModsVersion
from util.constants import *


def get_beat_saber_version(alias: str) -> Optional[BeatModsVersion]:
    """
    Gets the BeatMods Beat Saber version for a given alias
    :param alias: A Beat Saber version number
    :return: The BeatMods version for the given alias, or None if the version doesn't exist.
    """
    response = requests.get(BEAT_MODS_ALIASES)
    for version, aliases in response.json().items():
        if alias == version or alias in aliases:
            return BeatModsVersion(version, alias)
    return None


def get_latest_beat_saber_version() -> Optional[BeatModsVersion]:
    """
    Gets the latest Beat Saber version from BeatMods
    :return: The BeatMods version for the latest available alias
    """
    response = requests.get(BEAT_MODS_ALIASES)
    # flatten the list of aliases
    versions = [[BeatModsVersion(version, version)] + [BeatModsVersion(version, alias) for alias in aliases]
                for version, aliases in response.json().items()]
    flattened = [version for sublist in versions for version in sublist]
    return max(flattened)


def get_installed_version(install_path: Path) -> Optional[BeatModsVersion]:
    """
    Gets the installed Beat Saber version
    :param install_path: The Beat Saber install directory
    :return: The BeatMods version for the current Beat Saber install
    """
    # basic logic borrowed from ModAssistant.
    # https://github.com/Assistant/ModAssistant/blob/3b9dc222d0686e6c22ef83d65f498a6fe99f4897/ModAssistant/Classes/Utils.cs#L235
    version_file = install_path / "Beat Saber_Data" / "globalgamemanagers"
    if not version_file.exists():
        return None

    with version_file.open('rb') as data:
        file_content = data.read().decode("utf_8", "ignore")
    idx = file_content.index("public.app-category.games")
    # the version number starts 136 characters after this key and exists in a 32-byte chunk.
    ver_block = file_content[idx + 136:idx + 136 + 32]
    # trim to only the actual version number
    ver = re.search(VERSION_REGEX, ver_block).group(0)
    # we now have a valid alias, go fetch details from BeatMods
    return get_beat_saber_version(ver)
