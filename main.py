# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import db
import ui_orders
import ui_dictionaries


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("СпортФорм — Информационная система")
        self.geometry("1100x700")
        self.minsize(900, 600)

        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        dict_menu = tk.Menu(menubar, tearoff=0)
        dict_menu.add_command(
            label="Контрагенты",
            command=lambda: ui_dictionaries.open_dict(self, "contractors"))
        dict_menu.add_command(
            label="Продукция",
            command=lambda: ui_dictionaries.open_dict(self, "products"))
        dict_menu.add_command(
            label="Материалы",
            command=lambda: ui_dictionaries.open_dict(self, "materials"))
        dict_menu.add_command(
            label="Операции",
            command=lambda: ui_dictionaries.open_dict(self, "operations"))
        dict_menu.add_command(
            label="Спецификации",
            command=lambda: ui_dictionaries.open_dict(self, "specs"))
        menubar.add_cascade(label="Справочники", menu=dict_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="О программе",
            command=lambda: messagebox.showinfo(
                "О программе",
                "СпортФорм — информационная система предприятия\n© 2026"))
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        frame_orders = ttk.Frame(nb)
        nb.add(frame_orders, text="Заказы покупателей")
        ui_orders.build_orders_tab(frame_orders)

        if db.get_connection() is None:
            messagebox.showwarning(
                "Нет подключения",
                "Не удалось подключиться к БД sportform.\n"
                "Проверьте параметры в db.py и запустите PostgreSQL.")


if __name__ == "__main__":
    try:
        MainWindow().mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", str(e))