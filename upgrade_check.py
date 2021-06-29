import argparse
import itertools
import re
import textwrap
from pathlib import Path
from typing import List, Optional, Tuple, Union, Callable, Any, Iterable, Set

from pypref import SinglePreferences as Preferences
from texttable import Texttable

import util.beat_saber as bs
import util.available_mods as am
import util.installed_mods as im
from ui.console_table_ui import ConsoleTableUI
from util.constants import *
from model.beat_mods_version import BeatModsVersion
from model.mod import Mod

from ui.graphical_table_ui import GraphicalTableUI


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


TABLE_HEADERS = ["Name", "From BeatMods", "Upgradeable", "Old Version", "New Version", "Link"]
TABLE_ALIGN = ["c", "l", "l", "l", "l", "l"]
TABLE_DTYPE = [str, boolean_text, boolean_text, optional_text, optional_text, optional_text]


def safe_version(mod: Optional[Mod]) -> str:
    return mod.version if mod else None


def mod_name_sort_order(mod: Union[Mod, str]) -> str:
    name = mod if isinstance(mod, str) else mod.name
    if name == "BSIPA":
        return ""
    return name


def make_mod_diff_to_rows(mod_diff: List[Tuple[Mod, Optional[Mod]]], include_upgradeable: bool = True):
    """
    Converts a list of mod diffs to table rows
    """
    return [[old.name, old.version, safe_version(new), old.version, safe_version(new), old.link]
            for old, new in sorted(mod_diff, key=lambda x: mod_name_sort_order(x[0]))
            # if we want to include upgradeable mods, get everything. otherwise only get it if there's no new version
            if include_upgradeable or safe_version(new) is None]


def make_mod_list_to_rows(mods: List[Mod]):
    """
    Converts a list of mods to table rows, assuming they are not available on BeatMods. Since installed mods can yield
    a single mod object per file, this also filters down to uniquely named mods
    """
    unique_names = set(map(lambda x: x.name, mods))
    return [[mod_name, None, None, None, None, None] for mod_name in sorted(unique_names, key=mod_name_sort_order)]


def make_slicing_function(*slicers: slice) -> Callable[[List[Any]], List[Any]]:
    """
    Makes a slicing function that composes a new list out of various slices of the original list
    :param slicers: The slicers to use
    :return: A callable that can slice the new list
    """
    def closure(items: List[Any]) -> List[Any]:
        return list(itertools.chain.from_iterable(items[s] for s in slicers))
    return closure


def slice_columns(slicer_fn: Callable[[List[Any]], List[Any]],
                  rows: List[Any]) -> Iterable:
    """
    Gets a customizable slice of columns from a list of rows or column properties
    :param rows: The rows of the table, or a list of column properties. All rows should be of the same length.
    :param slicer_fn: A slicing function to use.
    :return: An iterable of the rows after slicing the columns.
    """
    # transpose to columns, then slice the collection of columns
    column_properties = list(zip(*rows))
    sliced_column_properties = slicer_fn(column_properties)
    # transpose back
    return list(zip(*sliced_column_properties))


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
    parser.add_argument("--no-upgrade-only", "-n", action="store_true", required=False,
                        help="Optional flag. Hides mods that have an upgrade available from Mod Assistant. This can "
                             "reduce clutter if you don't need or want a list of all your installed mods.")
    parser.add_argument("--show-versions", "-v", action="store_true", required=False,
                        help="Optional flag. Display installed and target version of each mod. Generally this is not "
                             "relevant and takes more space in the table, but it's a fun detail that's available "
                             "if you want it!")

    args = parser.parse_args()

    # postprocessing
    pref.update_preferences({PREF_INSTALL_DIRECTORY: str(args.install_path)})

    return args


def main(args: argparse.Namespace):
    # make the appropriate slicer function based on whether versions should be shown
    if args.show_versions:
        slicer_fn = make_slicing_function(slice(None))
    else:
        slicer_fn = make_slicing_function(slice(3), slice(-1, None))

    # slice headers and column metadata
    headers, aligns, dtypes = slice_columns(slicer_fn, [TABLE_HEADERS, TABLE_ALIGN, TABLE_DTYPE])

    # get the installed and target BeatMods version
    current_version = BeatModsVersion("1.13.4", "1.15.0")  # bs.get_installed_version(args.install_path)
    target_version = args.target if args.target else bs.get_latest_beat_saber_version()

    each_ui = list(map(lambda x: x(current_version, target_version, headers, aligns, dtypes),
                    [ConsoleTableUI, GraphicalTableUI]))

    if target_version <= current_version:
        msg = f"Target version ({target_version.alias}) must be newer than current version ({current_version.alias})."
        for ui in each_ui:
            ui.alert(msg)
        exit(1)

    each_ui[0].alert(f"Evaluating upgrade from {current_version.alias} to {target_version.alias}...")

    # get available mods for current and target version
    current_ver_mods = am.get_mods_for_version(current_version)
    target_ver_mods = am.get_mods_for_version(target_version)

    # verify there's a BSIPA install. if not, we're not on a modded install of Beat Saber
    bsipa = im.get_bsipa(args.install_path)
    # this will get a list of 0 or 1 BSIPA mods
    bsipa = im.intersect_against_available({bsipa}, current_ver_mods)[0]

    if not bsipa:
        for ui in each_ui:
            ui.alert("BSIPA is not installed.")
        exit(1)

    # find mods we have installed and detect which ones are on BeatMods for our current version
    installed_mods = im.get_installed_mods(args.install_path)
    installed_mods_on_beatmods, installed_mods_other = im.intersect_against_available(installed_mods, current_ver_mods)

    # find which of our installed mods have an available upgrade
    upgrade_diff = im.upgrade_diff(installed_mods_on_beatmods, target_ver_mods)

    mod_installer_rows = slice_columns(slicer_fn, make_mod_diff_to_rows(upgrade_diff, not args.no_upgrade_only))
    manual_mod_rows = slice_columns(slicer_fn, make_mod_list_to_rows(installed_mods_other))

    for ui in each_ui:
        ui.add_items(mod_installer_rows)
        ui.add_items(manual_mod_rows)
        ui.show()


if __name__ == "__main__":
    main(parse_args_and_preferences())
