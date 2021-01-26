import hashlib
from pathlib import Path

from typing import List, Tuple, Optional

from model.mod import Mod, FileHash


def _hash_file(file: Path) -> str:
    """
    Gets the MD5 hash of a file
    :param file: The file to hash
    :return: The hash of the file's content
    """
    with file.open('rb') as f:
        byte_data = f.read()
    m = hashlib.md5()
    m.update(byte_data)

    return m.hexdigest().lower()


def get_bsipa(install_dir: Path) -> Mod:
    """
    Gets the currently installed version of BSIPA
    :return: The installed version of BSIPA
    """
    injector_path = install_dir / "Beat Saber_Data" / "Managed" / "IPA.Injector.dll"
    if injector_path.exists():
        injector_hash = _hash_file(injector_path)
        return Mod("BSIPA", None, None, [[FileHash(str(injector_path), injector_hash)]])


def get_installed_mods(install_dir: Path) -> List[Mod]:
    """
    Gets a list of installed mods. If a mod has multiple files associated dll/manifest files, this may yield one mod
    for each, even though there should be fewer logical mods.
    :return: A list of non-BSIPA mods
    """
    mod_locations = ["IPA/Pending/Plugins", "IPA/Pending/Libs", "Plugins", "Libs"]
    mod_paths = [install_dir / subdir for subdir in mod_locations]

    installed_mods = []
    for path in mod_paths:
        if path.exists():
            for file in path.iterdir():
                # skip subdirs if there is any
                if file.is_file() and (file.suffix == ".dll" or file.suffix == ".manifest"):
                    file_hash = _hash_file(file)
                    installed_mods.append(Mod(file.stem, None, None, [[FileHash(str(file), file_hash)]]))

    return installed_mods


def intersect_against_available(installed_mods: List[Mod],
                                available_mods_for_version: List[Mod]) -> Tuple[List[Mod], List[Mod]]:
    """
    Partitions a list of installed mods into mods that are available on BeatMods and a list of mods that are not
    :param installed_mods: A list of installed mods
    :param available_mods_for_version: A list of available mods
    :return: A list of mods available on BeatMods and a list of mods that are not
    """
    # for each AVAILABLE mod, check them against all the installed mods
    installed_available = []
    installed_mods_found_available = []

    for installed in installed_mods:
        if installed not in installed_mods_found_available:
            for available in available_mods_for_version:
                if available.do_file_hashes_match(installed):
                    # found match
                    installed_mods_found_available.append(installed)
                    # keep the list of available installed mods unique
                    if available not in installed_available:
                        installed_available.append(available)
    # filter to any installed mods with no matching available mod
    installed_not_available = [installed for installed in installed_mods
                               if installed not in installed_mods_found_available]
    return installed_available, installed_not_available


def upgrade_diff(installed_mods: List[Mod], available_mods: List[Mod]) -> List[Tuple[Mod, Optional[Mod]]]:
    """
    Pairs installed mods to available mods in another version. If there isn't an available version of the mod,
    the second value will be None
    :param installed_mods: List of installed mods
    :param available_mods: List of available mods
    :return: List of pairs of mods (old, new)
    """
    pairs = []
    found_match = []
    for installed in installed_mods:
        if installed not in found_match:
            for available in available_mods:
                if installed.do_names_match(available):
                    pairs.append((installed, available))
                    found_match.append(installed)
                    break
            # if no match, record that as well
            if installed not in found_match:
                pairs.append((installed, None))
    return pairs
