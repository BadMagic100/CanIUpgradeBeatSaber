import tkinter as tk
from tkinter import messagebox as mb
import webbrowser
from tkinter import ttk
from typing import List, Callable, Any, Iterable

from model.beat_mods_version import BeatModsVersion
from ui.base_table_ui import BaseTableUI


class GraphicalTableUI(BaseTableUI):

    __ALIGNMENT_LOOKUP = {
        'c': tk.CENTER,
        'l': tk.W,
        'r': tk.E
    }

    def __treeview_click(self, event):
        if self._table.identify_region(event.x, event.y) == "separator":
            return "break"

    def __treeview_motion(self, event):
        if self._table.identify_region(event.x, event.y) == "separator":
            return "break"

    def __treeview_link(self, event):
        *_, last = iter(self._table['columns'])
        clicked_col = self._table.identify_column(event.x)
        if clicked_col == "#" + last:
            selected_id = self._table.selection()
            selected_item = self._table.item(selected_id, "values")
            url = selected_item[-1]
            if url != "-":
                webbrowser.open(url)

    def __init__(self, old_version: BeatModsVersion, new_version: BeatModsVersion,
                 header: List[str], align: List[str], dtype: List[Callable[[Any], str]],
                 width: int = 1000, height: int = 600):
        self._dtypes = dtype

        self._gui = gui = tk.Tk()
        gui.title(f"Beat Saber Mod Upgrade - {old_version.alias} to {new_version.alias}")
        gui.geometry(f"{width}x{height}")

        self._table = table = ttk.Treeview(gui, selectmode="browse", show="headings",
                                           columns=tuple(range(1, len(header) + 1)))

        scroll = ttk.Scrollbar(gui, orient=tk.VERTICAL, command=table.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        table.configure(yscrollcommand=scroll.set)

        for i, (h, a) in enumerate(zip(header, align), start=1):
            # link col is always last, allocate most space for that one
            table.column(str(i), anchor=GraphicalTableUI.__ALIGNMENT_LOOKUP[a], stretch=(i == len(header)))
            table.heading(str(i), text=h)

        table.bind("<Button-1>", self.__treeview_click)
        table.bind("<Motion>", self.__treeview_motion)
        table.bind("<Double-1>", self.__treeview_link)
        table.tag_configure("odd", background="red")
        table.pack(expand=True, fill=tk.BOTH)

        gui.withdraw()

    def add_items(self, items: Iterable[Iterable]):
        for item in items:
            mapped_row = list(map(lambda x: x[0](x[1]), zip(self._dtypes, item)))
            self._table.insert("", tk.END, values=mapped_row)

    def show(self):
        self._gui.deiconify()
        self._gui.mainloop()

    def alert(self, message: str):
        mb.showerror(message=message)
