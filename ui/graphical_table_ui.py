import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import webbrowser
from tkinter import ttk
from typing import List, Callable, Any, Iterable, Optional

from model.beat_mods_version import BeatModsVersion
from ui.base_table_ui import BaseTableUI


class GraphicalTableUI(BaseTableUI):
    __ALIGNMENT_LOOKUP = {
        'c': tk.CENTER,
        'l': tk.W,
        'r': tk.E
    }

    def __is_mouse_in_last_column(self, mouse_x):
        *_, last = iter(self._table['columns'])
        col = self._table.identify_column(mouse_x)
        return col == f'#{last}'

    def __get_mouse_row_link_text(self, mouse_y):
        row_id = self._table.identify_row(mouse_y)
        row_values = self._table.item(row_id, "values")
        return row_values[-1]

    def __treeview_click(self, event):
        region = self._table.identify_region(event.x, event.y)
        if region == "cell" and self.__is_mouse_in_last_column(event.x):
            link_text = self.__get_mouse_row_link_text(event.y)
            if link_text != "-":
                webbrowser.open(link_text)
        if self._table.identify_region(event.x, event.y) == "separator":
            return "break"

    def __treeview_motion(self, event):
        region = self._table.identify_region(event.x, event.y)
        if (region == "cell" and self.__is_mouse_in_last_column(event.x)
                and self.__get_mouse_row_link_text(event.y) != "-"):
            self._gui.config(cursor="hand2")
        else:
            self._gui.config(cursor="arrow")

        if region == "separator":
            return "break"

    def __init__(self, header: List[str], align: List[str], dtype: List[Callable[[Any], str]],
                 width: int = 1000, height: int = 600):
        self._dtypes = dtype

        # configure root window
        self._gui = gui = tk.Tk()
        gui.geometry(f"{width}x{height}")

        # set up the data table
        self._table = table = ttk.Treeview(gui, selectmode="none", show="headings",
                                           columns=tuple(range(1, len(header) + 1)))

        for i, (h, a) in enumerate(zip(header, align), start=1):
            # first column is always the name, make it wider than others
            col_width = 200 if i == 1 else 120
            # allow the last column (link) to stretch out to the screen bounds
            should_stretch = i == len(header)
            table.column(str(i), anchor=GraphicalTableUI.__ALIGNMENT_LOOKUP[a], stretch=should_stretch,
                         width=col_width, minwidth=col_width)
            table.heading(str(i), text=h)

        table.bind("<Button-1>", self.__treeview_click)
        table.bind("<Motion>", self.__treeview_motion)

        # add scrollbars for the treeview
        yscroll = ttk.Scrollbar(gui, orient=tk.VERTICAL, command=table.yview)
        xscroll = ttk.Scrollbar(gui, orient=tk.HORIZONTAL, command=table.xview)
        table.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        # do layout
        yscroll.grid(row=0, column=1, sticky=tk.NS)
        xscroll.grid(row=1, column=0, sticky=tk.EW)
        table.grid(row=0, column=0, sticky=tk.NSEW)
        gui.rowconfigure(0, weight=1)
        gui.columnconfigure(0, weight=1)

        # start minimized so we're allowed to show messageboxes first
        gui.withdraw()

    def set_versions(self, old_version: BeatModsVersion, new_version: BeatModsVersion):
        self._gui.title(f"Beat Saber Mod Upgrade - {old_version.alias} to {new_version.alias}")

    def add_items(self, items: Iterable[Iterable]):
        for item in items:
            mapped_row = list(map(lambda x: x[0](x[1]), zip(self._dtypes, item)))
            self._table.insert("", tk.END, values=mapped_row)

    def show(self):
        self._gui.deiconify()
        self._gui.mainloop()

    def alert(self, message: str):
        mb.showerror(message=message)

    def prompt_for_directory(self, message: Optional[str] = None) -> Optional[str]:
        return fd.askdirectory(title=message, mustexist=True)
