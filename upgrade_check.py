import argparse
import re
import textwrap
from pathlib import Path
from typing import List, Optional, Tuple

from pypref import SinglePreferences as Preferences
from texttable import Texttable

import util.beat_saber as bs
import util.available_mods as am
import util.installed_mods as im
from util.constants import *
from model.beat_mods_version import BeatModsVersion
from model.mod import Mod


def validate_beat_saber_version(value: str) -> BeatModsVersion:
    """
    Validates and converts a BeatModsVersion from a string input, or raises a validation error.
    :param value: The raw command line argument
    :return: A valid BeatModsVersion represented by the input
    """
    # 1.1.0p1 is a valid version, so we should assume that the build can contain non-numeric characters
    if re.match(VERSION_REGEX, value):
        version = bs.get_beat_saber_version(value)
        if version:
            return version
    raise argparse.ArgumentTypeError(f"{value} is not a valid Beat Saber version or alias, or is not available "
                                     "on BeatMods.")


def validate_install_dir(value: str) -> Path:
    """
    Validates and converts an install Path from a string input, or raises a validation error
    :param value: The raw command line argument
    :return:
    """
    path = Path(value)
    if path.exists() and bs.get_installed_version(path):
        return path
    raise argparse.ArgumentTypeError(f"{value} is not a valid Beat Saber install directory, or your installed version "
                                     "is not available on BeatMods.")


class NewlineSmartFormatter(argparse.HelpFormatter):
    """
    Quick and dirty formatter to format each newline-separated paragraph separately
    """
    def _fill_text(self, text, width, indent):
        return "\n".join([textwrap.fill(line, width) for line
                          in textwrap.indent(textwrap.dedent(text), indent).splitlines()])


def boolean_text(text: Optional[str]) -> str:
    """
    Formats a string as yes/no depending on whether it is present
    :param text: The text to format
    :return: "Yes" if text is truthy, otherwise "No"
    """
    return 'Yes' if text else 'No'


def optional_text(text: Optional[str]) -> str:
    """
    Formats a falsey strings as "-"
    :param text: The text to format
    :return: "-" if the text is falsey, otherwise the original text
    """
    return text if text else "-"


TABLE_HEADERS = ["Name", "Available on BeatMods", "Upgrade Available", "Source Version", "Target Version", "Link"]
TABLE_FORMAT = Texttable.HEADER | Texttable.VLINES | Texttable.HLINES
TABLE_ALIGN = ["c", "l", "l", "l", "l", "l"]
TABLE_DTYPE = ['t', boolean_text, boolean_text, optional_text, optional_text, optional_text]


def safe_version(mod: Optional[Mod]) -> str:
    return mod.version if mod else None


def mod_name_sort_order(mod: Mod) -> str:
    if mod.name == "BSIPA":
        return ""
    return mod.name


def make_mod_diff_to_rows(mod_diff: List[Tuple[Mod, Optional[Mod]]]):
    """
    Converts a list of mod diffs to table rows
    """
    return [[old.name, old.version, safe_version(new), old.version, safe_version(new), old.link]
            for old, new in sorted(mod_diff, key=lambda x: mod_name_sort_order(x[0]))]


def make_mod_list_to_rows(mods: List[Mod]):
    """
    Converts a list of mods to table rows, assuming they are not available on BeatMods
    """
    return [[mod.name, None, None, None, None, None] for mod in sorted(mods, key=mod_name_sort_order)]


def parse_args_and_preferences() -> argparse.Namespace:
    """
    Parses command line arguments and persistent preferences
    :return: The parsed command line arguments
    """
    # preprocessing
    pref = Preferences(filename=PREFERENCES_FILE)
    previously_provided_install_dir = pref.get(PREF_INSTALL_DIRECTORY, None)

    # parsing
    parser = argparse.ArgumentParser(description="This script can help you determine if it's safe to upgrade your PC"
                                                 " installation of Beat Saber by telling you which of your installed"
                                                 " mods have a known upgrade available in your target version. It"
                                                 " cannot tell you anything about mods that are not available on Mod"
                                                 " Assistant, nor can it tell you if a mod's functionality has been"
                                                 " replaced by a new mod or the base game.\n\n"
                                                 "====================\n\nIf a mod you want to keep doesn't have an"
                                                 " upgrade available, here are some things you can try to help you"
                                                 " decide if you should upgrade:\n\n"
                                                 "* Check beatmods.com: This is the source of truth for Mod Assistant."
                                                 " You can use this to help find new mods that might replace the "
                                                 " functionality you're looking for.\n\n"
                                                 "* Check the '#pc-mods' channel on the BSMG Discord: This can be a"
                                                 " good source for mods, especially if they're new or otherwise not yet"
                                                 " available in Mod Assistant.\n\n"
                                                 "* Check the mod's GitHub page: This may contain information about"
                                                 " upcoming releases or have beta version available. At a minimum,"
                                                 " you can usually tell if a mod is actively being developed.",
                                     formatter_class=NewlineSmartFormatter)
    parser.add_argument("--target", "-t", type=validate_beat_saber_version,
                        help="The version to upgrade to. If not provided, defaults to the latest version of Beat "
                             "Saber available on BeatMods.")
    parser.add_argument("--install-path", "-p", required=not previously_provided_install_dir, type=validate_install_dir,
                        default=previously_provided_install_dir,
                        help="The install directory of Beat Saber. If not provided, defaults to the directory used "
                             "in the previous run. Required for the first run. You can find this in Mod Assistant's "
                             "settings if you're not sure. If there's a space in the path, wrap the path in "
                             "quotes (\")")

    args = parser.parse_args()

    # postprocessing
    pref.update_preferences({PREF_INSTALL_DIRECTORY: str(args.install_path)})

    return args


def main(args: argparse.Namespace):
    # get the installed and target BeatMods version
    current_version = bs.get_installed_version(args.install_path)
    target_version = args.target if args.target else bs.get_latest_beat_saber_version()

    if target_version <= current_version:
        print(f"Target version ({target_version.alias}) must be newer than current version ({current_version.alias}).")
        exit(1)

    print(f"Evaluating upgrade from {current_version.alias} to {target_version.alias}...")

    # get available mods for current and target version
    current_ver_mods = am.get_mods_for_version(current_version)
    target_ver_mods = am.get_mods_for_version(target_version)

    # verify there's a BSIPA install. if not, we're not on a modded install of Beat Saber
    bsipa = im.get_bsipa(args.install_path)
    # this will get a list of 0 or 1 BSIPA mods
    bsipa = im.intersect_against_available([bsipa], current_ver_mods)[0]

    if not bsipa:
        print("BSIPA is not installed.")
        exit(1)

    # there's an installed BSIPA, take it out of the list for use
    bsipa = bsipa[0]
    print(f"Found installed BSIPA version: {str(bsipa)}")

    # find mods we have installed and detect which ones are on BeatMods for our current version
    installed_mods = im.get_installed_mods(args.install_path)
    installed_mods_on_beatmods, installed_mods_other = im.intersect_against_available(installed_mods, current_ver_mods)

    # find which of our installed mods have an available upgrade
    upgrade_diff = im.upgrade_diff(installed_mods_on_beatmods, target_ver_mods)

    # format everything into a nice table and print it. List online mods first.
    table = Texttable()
    table.header(TABLE_HEADERS)
    table.set_cols_align(TABLE_ALIGN)
    table.set_cols_dtype(TABLE_DTYPE)
    table.set_deco(TABLE_FORMAT)
    table.set_max_width(120)
    table.add_rows(make_mod_diff_to_rows(upgrade_diff), False)
    table.add_rows(make_mod_list_to_rows(installed_mods_other), False)
    print(table.draw())


if __name__ == "__main__":
    main(parse_args_and_preferences())
