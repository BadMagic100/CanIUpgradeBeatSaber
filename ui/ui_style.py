from enum import Enum


class UIStyle(Enum):
    GRAPHICAL = "graphical"
    CONSOLE = "console"

    def __str__(self):
        return self.value
