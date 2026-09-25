# ui_orders.py
import tkinter as tk
from tkinter import ttk, messagebox
import db, queries
import ui_order_card


def build_orders_tab(parent):
    # ---------- Панель поиска и фильтрации ----------
    frm = ttk.LabelFrame(parent, text="Поиск и фильтрация")
    frm.pack(fill="x", padx=8, pady=6)

    ttk.Label(frm, text="Номер заказа:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
    ent_no = ttk.Entry(frm, width=15)
    ent_no.grid(row=0, column=1, padx=4, pady=4)

    ttk.Label(frm, text="Покупатель:").grid(row=0, column=2, padx=4, pady=4, sticky="e")
    ent_cust = ttk.Entry(frm, width=30)
    ent_cust.grid(row=0, column=3, padx=4, pady=4)

    ttk.Label(frm, text="Статус:").grid(row=0, column=4, padx=4, pady=4, sticky="e")
    cmb_status = ttk.Combobox(frm, values=["Все"] + queries.STATUSES,
                              state="readonly", width=18)
    cmb_status.set("Все")
    cmb_status.grid(row=0, column=5, padx=4, pady=4)

    btn_search = ttk.Button(frm, text="Найти")
    btn_search.grid(row=0, column=6, padx=6)

    btn_reset = ttk.Button(frm, text="Сброс")
    btn_reset.grid(row=0, column=7, padx=2)

    # ---------- Таблица ----------
    cols = ("order_no", "order_date", "customer", "product",
            "quantity", "status", "total")
    headers = ("Номер", "Дата", "Покупатель", "Продукция",
               "Кол-во", "Статус", "Сумма")
    widths = (80, 90, 180, 240, 70, 130, 110)

    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill="both", expand=True, padx=8, pady=6)

    tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
    for c, h, w in zip(cols, headers, widths):
        tree.heading(c, text=h)
        tree.column(c, width=w, anchor="w")
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    # ---------- Кнопки ----------
    btns = ttk.Frame(parent)
    btns.pack(fill="x", padx=8, pady=4)

    btn_open    = ttk.Button(btns, text="Открыть карточку")
    btn_new     = ttk.Button(btns, text="Новый заказ")
    btn_refresh = ttk.Button(btns, text="Обновить")
    btn_open.pack(side="left", padx=4)
    btn_new.pack(side="left", padx=4)
    btn_refresh.pack(side="left", padx=4)

    # ---------- Загрузка ----------
    def load_orders():
        try:
            order_no = ent_no.get().strip() or None
            customer = ent_cust.get().strip() or None
            status = cmb_status.get()
            status = None if status == "Все" else status

            rows = db.execute(queries.ORDERS_LIST, {
                "order_no": order_no,
                "customer": customer,
                "status": status,
            }, fetch=True) or []

            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert("", "end", values=r)
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    btn_search.config(command=load_orders)
    btn_refresh.config(command=load_orders)

    def reset():
        ent_no.delete(0, tk.END)
        ent_cust.delete(0, tk.END)
        cmb_status.set("Все")
        load_orders()

    btn_reset.config(command=reset)

    def open_card():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Карточка заказа", "Выберите заказ из списка.")
            return
        order_no = tree.item(sel[0])["values"][0]
        ui_order_card.open_order_card(parent, order_no, on_change=load_orders)

    btn_open.config(command=open_card)
    tree.bind("<Double-1>", lambda e: open_card())

    def new_order():
        ui_order_card.open_new_order(parent, on_change=load_orders)

    btn_new.config(command=new_order)

    load_orders()