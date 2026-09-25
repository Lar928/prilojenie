# ui_dictionaries.py
import tkinter as tk
from tkinter import ttk, messagebox
import db, queries


DICT_CONFIG = {
    "contractors": {
        "title": "Контрагенты",
        "sql": queries.ALL_CONTRACTORS,
        "cols": ("ID", "Наименование", "ИНН", "Адрес", "Телефон", "Тип"),
        "widths": (70, 200, 110, 260, 130, 100),
    },
    "products": {
        "title": "Продукция",
        "sql": queries.ALL_PRODUCTS,
        "cols": ("Код", "Наименование", "Ед.", "Цена"),
        "widths": (70, 280, 60, 100),
    },
    "materials": {
        "title": "Материалы",
        "sql": queries.ALL_MATERIALS,
        "cols": ("Код", "Наименование", "Ед.", "Цена закупки", "Поставщик"),
        "widths": (70, 280, 60, 110, 220),
    },
    "operations": {
        "title": "Технологические операции",
        "sql": queries.ALL_OPERATIONS,
        "cols": ("Код", "Наименование", "Стоимость"),
        "widths": (70, 300, 110),
    },
    "specs": {
        "title": "Спецификации продукции",
        "sql": queries.ALL_SPECS,
        "cols": ("Код продукта", "Продукция", "Код материала",
                 "Материал", "Количество"),
        "widths": (100, 240, 110, 260, 100),
    },
}


def open_dict(parent, key):
    cfg = DICT_CONFIG.get(key)
    if not cfg:
        return

    try:
        rows = db.execute(cfg["sql"], fetch=True) or []
    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
        return

    win = tk.Toplevel(parent)
    win.title(cfg["title"])
    win.geometry("1000x600")

    ttk.Label(win, text=cfg["title"], font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10, pady=8)

    frame = ttk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=6)

    tree = ttk.Treeview(frame, columns=cfg["cols"], show="headings")
    for c, w in zip(cfg["cols"], cfg["widths"]):
        tree.heading(c, text=c)
        tree.column(c, width=w, anchor="w")
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    for r in rows:
        tree.insert("", "end", values=r)

    ttk.Button(win, text="Закрыть", command=win.destroy)\
        .pack(anchor="e", padx=10, pady=8)