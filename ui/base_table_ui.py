from abc import ABC, abstractmethod
from typing import Iterable, Optional

from model.beat_mods_version import BeatModsVersion


class BaseTableUI(ABC):
    @abstractmethod
    def set_versions(self, old_version: BeatModsVersion, new_version: BeatModsVersion):
        """
        Sets the Beat Saber versions for display purposes.
        :param old_version: The old/current version.
        :param new_version: The new/target version.
        """

    @abstractmethod
    def add_items(self, items: Iterable[Iterable]):
        """
        Add items to the table.
        :param items: The items to add to the table. Should be the same number of columns as the header.
        """

    @abstractmethod
    def show(self):
        """
        Renders the UI.
        """

    @abstractmethod
    def alert(self, message: str):
        """
        Displays a message to the user.
        :param message: The message to display.
        """

    @abstractmethod
    def prompt_for_directory(self, message: Optional[str] = None) -> Optional[str]:
        """
        Prompts a user for a directory.
        :param message: An optional prompt message.
        :return: The directory path provided by the user
        """
