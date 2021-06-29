from abc import ABC, abstractmethod
from typing import Iterable


class BaseTableUI(ABC):
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
