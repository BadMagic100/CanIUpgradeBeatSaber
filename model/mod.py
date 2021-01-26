from typing import List, Optional
from copy import deepcopy


class FileHash:
    """
    Represents a vile and its hash, for comparison
    """

    def __init__(self, file: str, md5_hash: str):
        """
        Initializes a FileHash
        :param file: The file path. Can be absolute or relative to the install directory
        :param md5_hash: The hash of the file
        """
        self._file = file
        self._md5_hash = md5_hash

    @property
    def file(self) -> str:
        """
        The file path. Can be absolute or relative to the install directory
        """
        return self._file

    @property
    def hash(self) -> str:
        """
        The hash of the file
        """
        return self._md5_hash

    def __eq__(self, other):
        if not isinstance(other, FileHash):
            return False

        if (self is None and other is not None) or (self is not None and other is None):
            return False

        # doesn't matter where the file is actually at, 2 files are equal if they have the same hash
        return self.hash == other.hash

    def __str__(self):
        return f"{self.file} md5={self.hash}"

    def __repr__(self):
        return "<" + str(self) + ">"


class Mod:

    def __init__(self, name: str, version: Optional[str], link: Optional[str], files: List[List[FileHash]]):
        """
        Initializes a mod
        :param name: The name of the mod
        :param version: The version of the mod, if it's on BeatMods
        :param link: The link to the mod page, if it's on BeatMods
        :param files: A list of lists of FileHash objects
        """
        self._name = name
        self._version = version
        self._link = link
        self._files = files

    @property
    def name(self) -> str:
        """
        The name of the mod
        """
        return self._name

    @property
    def version(self) -> Optional[str]:
        """
        The version of the mod, if it's on BeatMods
        """
        return self._version

    @property
    def link(self) -> Optional[str]:
        """
        A link to the mod's home page, if it's on BeatMods
        """
        return self._link

    @property
    def files(self) -> List[List[FileHash]]:
        """
        Files installed with the mod, grouped by logical install download zips
        """
        return deepcopy(self._files)

    def do_names_match(self, other):
        """
        Checks if 2 mods have the same
        :param other: The other mod
        :return: Whether the mods are the same
        """
        # 2 mods can be considered equal if they have the same name
        return self.name == other.name

    def do_file_hashes_match(self, other):
        """
        Checks if 2 mods have any same files
        :param other: The other mod
        :return: Whether the mods are the same
        """
        # 2 mods can be considered equal if any of their files have the same hash
        # flatten both mod lists for convenient
        self_files_flat = [file for sublist in self._files for file in sublist]
        other_files_flat = [file for sublist in other.files for file in sublist]

        return any(file in other_files_flat for file in self_files_flat)

    def __str__(self):
        return f"{self.name} v{self.version}"

    def __repr__(self):
        return "<" + str(self) + ">"
