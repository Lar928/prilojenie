# ui_order_card.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import db, queries


# ============================================================
# Карточка существующего заказа
# ============================================================
def open_order_card(parent, order_no, on_change=None):
    try:
        row = db.execute(queries.ORDER_BY_NO, (order_no,), fetch=True)
    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
        return

    if not row:
        messagebox.showwarning("Не найдено",
                               f"Заказ {order_no} отсутствует в базе.")
        return

    (order_no, order_date, customer_id, customer_name,
     status, product_code, product_name, quantity, price, total) = row[0]

    win = tk.Toplevel(parent)
    win.title(f"Заказ {order_no}")
    win.geometry("640x520")
    win.transient(parent)
    win.grab_set()

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    def add_label(r, label, value):
        ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=4, pady=4)
        ttk.Label(frm, text=str(value)).grid(row=r, column=1, sticky="w", padx=4, pady=4)

    add_label(0, "Номер заказа:", order_no)
    add_label(1, "Дата:", order_date)
    add_label(2, "Покупатель:", customer_name)
    add_label(3, "Продукция:", product_name)

    qty_var = tk.StringVar(value=str(quantity))
    ttk.Label(frm, text="Количество:").grid(row=4, column=0, sticky="e", padx=4, pady=4)
    ttk.Entry(frm, textvariable=qty_var).grid(row=4, column=1, sticky="we", padx=4, pady=4)

    add_label(5, "Цена:", price)

    total_var = tk.StringVar(value=str(total))
    ttk.Label(frm, text="Сумма:").grid(row=6, column=0, sticky="e", padx=4, pady=4)
    ttk.Label(frm, textvariable=total_var, font=("Arial", 10, "bold"))\
        .grid(row=6, column=1, sticky="w", padx=4, pady=4)

    def recalc(*_):
        try:
            q = int(qty_var.get())
            if q > 0:
                total_var.set(f"{float(price) * q:.2f}")
            else:
                total_var.set("0.00")
        except ValueError:
            total_var.set("0.00")

    qty_var.trace_add("write", recalc)

    status_var = tk.StringVar(value=status)
    ttk.Label(frm, text="Статус:").grid(row=7, column=0, sticky="e", padx=4, pady=4)
    ttk.Combobox(frm, textvariable=status_var,
                 values=queries.STATUSES, state="readonly")\
        .grid(row=7, column=1, sticky="we", padx=4, pady=4)

    # ---------- Производственные заказы ----------
    prod_frame = ttk.LabelFrame(frm, text="Производственные заказы", padding=6)
    prod_frame.grid(row=8, column=0, columnspan=2, sticky="we", padx=4, pady=8)

    prod_tree = ttk.Treeview(prod_frame,
                             columns=("no", "start", "qty", "status"),
                             show="headings", height=4)
    for c, h, w in [("no", "Номер", 90), ("start", "Дата запуска", 110),
                    ("qty", "Кол-во", 70), ("status", "Статус", 130)]:
        prod_tree.heading(c, text=h)
        prod_tree.column(c, width=w)
    prod_tree.pack(fill="x")

    def reload_prod():
        try:
            rows = db.execute(queries.PRODUCTION_BY_ORDER, (order_no,), fetch=True) or []
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        prod_tree.delete(*prod_tree.get_children())
        for r in rows:
            prod_tree.insert("", "end", values=r)

    def create_production():
        try:
            qty = int(qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть > 0.")
            return

        try:
            next_no = db.execute(queries.NEXT_PRODUCTION_NO, fetch=True)[0][0]
            db.execute(queries.INSERT_PRODUCTION_ORDER,
                       (next_no, order_no, date.today(), qty, "Запланирован"))
            messagebox.showinfo("Готово",
                                f"Производственный заказ {next_no} создан.")
            reload_prod()
        except Exception as e:
            messagebox.showerror("Ошибка создания", str(e))

    ttk.Button(prod_frame, text="Создать производственный заказ",
               command=create_production).pack(pady=4, anchor="w")

    reload_prod()

    # ---------- Сохранение ----------
    def save():
        try:
            q = int(qty_var.get())
            if q <= 0:
                raise ValueError("Количество должно быть больше нуля.")
        except ValueError as e:
            messagebox.showerror("Неверное количество", str(e))
            return

        try:
            db.execute(queries.UPDATE_ORDER_ITEM_QTY, (q, order_no, product_code))
            db.execute(queries.UPDATE_ORDER_STATUS, (status_var.get(), order_no))
            messagebox.showinfo("Сохранено", "Изменения сохранены.")
            if on_change:
                on_change()
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    ttk.Button(frm, text="Сохранить", command=save)\
        .grid(row=9, column=0, padx=4, pady=10)
    ttk.Button(frm, text="Закрыть", command=win.destroy)\
        .grid(row=9, column=1, sticky="e", padx=4, pady=10)


# ============================================================
# Создание нового заказа
# ============================================================
def open_new_order(parent, on_change=None):
    win = tk.Toplevel(parent)
    win.title("Новый заказ покупателя")
    win.geometry("560x460")
    win.transient(parent)
    win.grab_set()

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    try:
        customers = db.execute(queries.CUSTOMERS, fetch=True) or []
        products  = db.execute(queries.PRODUCTS,  fetch=True) or []
        next_no   = db.execute(queries.NEXT_ORDER_NO, fetch=True)[0][0]
    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
        win.destroy()
        return

    if not customers:
        messagebox.showwarning("Нет покупателей",
                               "В базе нет контрагентов типа «Покупатель».")
        win.destroy()
        return
    if not products:
        messagebox.showwarning("Нет продукции",
                               "В базе отсутствует продукция.")
        win.destroy()
        return

    ttk.Label(frm, text="Номер заказа:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
    ent_no = ttk.Entry(frm, width=22)
    ent_no.insert(0, next_no)
    ent_no.grid(row=0, column=1, sticky="we", padx=4, pady=4)

    ttk.Label(frm, text="Дата:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
    ent_date = ttk.Entry(frm, width=22)
    ent_date.insert(0, date.today().strftime("%d.%m.%Y"))
    ent_date.grid(row=1, column=1, sticky="we", padx=4, pady=4)

    ttk.Label(frm, text="Покупатель:").grid(row=2, column=0, sticky="e", padx=4, pady=4)
    cmb_cust = ttk.Combobox(frm, state="readonly", width=42,
                            values=[f"{c[0]} — {c[1]}" for c in customers])
    cmb_cust.grid(row=2, column=1, sticky="we", padx=4, pady=4)

    ttk.Label(frm, text="Продукция:").grid(row=3, column=0, sticky="e", padx=4, pady=4)
    cmb_prod = ttk.Combobox(frm, state="readonly", width=42,
                            values=[f"{p[0]} — {p[1]} — {p[2]} ₽" for p in products])
    cmb_prod.grid(row=3, column=1, sticky="we", padx=4, pady=4)

    ttk.Label(frm, text="Количество:").grid(row=4, column=0, sticky="e", padx=4, pady=4)
    ent_qty = ttk.Entry(frm, width=22)
    ent_qty.grid(row=4, column=1, sticky="we", padx=4, pady=4)

    total_var = tk.StringVar(value="0.00")
    ttk.Label(frm, text="Сумма:").grid(row=5, column=0, sticky="e", padx=4, pady=4)
    ttk.Label(frm, textvariable=total_var, font=("Arial", 11, "bold"))\
        .grid(row=5, column=1, sticky="w", padx=4, pady=4)

    def recalc(*_):
        try:
            qty = int(ent_qty.get() or 0)
            idx = cmb_prod.current()
            if qty > 0 and idx >= 0:
                price = float(products[idx][2])
                total_var.set(f"{price * qty:.2f}")
            else:
                total_var.set("0.00")
        except ValueError:
            total_var.set("0.00")

    ent_qty.bind("<KeyRelease>", recalc)
    cmb_prod.bind("<<ComboboxSelected>>", recalc)

    def save():
        order_no = ent_no.get().strip()
        if not order_no:
            messagebox.showerror("Ошибка", "Укажите номер заказа.")
            return
        if cmb_cust.current() < 0:
            messagebox.showerror("Ошибка", "Выберите покупателя.")
            return
        if cmb_prod.current() < 0:
            messagebox.showerror("Ошибка", "Выберите продукцию.")
            return
        try:
            qty = int(ent_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Количество должно быть целым числом > 0.")
            return

        try:
            parts = ent_date.get().split(".")
            d = date(int(parts[2]), int(parts[1]), int(parts[0]))
        except Exception:
            messagebox.showerror("Ошибка",
                                 "Дата должна быть в формате ДД.ММ.ГГГГ.")
            return

        customer_id  = customers[cmb_cust.current()][0]
        product_code = products[cmb_prod.current()][0]

        exists = db.execute(queries.ORDER_EXISTS, (order_no,), fetch=True)
        if exists:
            messagebox.showerror("Ошибка",
                                 f"Заказ с номером {order_no} уже существует.")
            return

        try:
            db.execute(queries.INSERT_ORDER, (order_no, d, customer_id, "Новый"))
            db.execute(queries.INSERT_ORDER_ITEM, (order_no, product_code, qty))
            messagebox.showinfo("Готово", f"Заказ {order_no} создан.")
            if on_change:
                on_change()
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    ttk.Button(frm, text="Создать", command=save)\
        .grid(row=6, column=0, padx=4, pady=12)
    ttk.Button(frm, text="Отмена", command=win.destroy)\
        .grid(row=6, column=1, sticky="e", padx=4, pady=12)