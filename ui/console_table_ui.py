from typing import Iterable, List, Callable, Any

from texttable import Texttable

from model.beat_mods_version import BeatModsVersion
from ui.base_table_ui import BaseTableUI


class ConsoleTableUI(BaseTableUI):
    __TABLE_FORMAT = Texttable.HEADER | Texttable.VLINES | Texttable.HLINES

    def __init__(self, old_version: BeatModsVersion, new_version: BeatModsVersion,
                 header: List[str], align: List[str], dtype: List[Callable[[Any], str]]):
        print(f"Evaluating upgrade from {old_version.alias} to {new_version.alias}...")

        self._table = table = Texttable()
        table.header(header)
        table.set_cols_align(align)
        table.set_cols_dtype(dtype)
        table.set_deco(ConsoleTableUI.__TABLE_FORMAT)
        table.set_max_width(120)

    def show(self):
        print(self._table.draw())

    def alert(self, message: str):
        print(message)

    def add_items(self, items: Iterable[Iterable]):
        self._table.add_rows(items, False)
