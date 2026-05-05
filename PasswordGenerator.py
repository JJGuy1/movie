import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

# Имя файла для сохранения истории
HISTORY_FILE = "password_history.json"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("750x500")
        self.root.resizable(True, True)

        # Переменные для хранения состояния
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        # История паролей (список словарей)
        self.history = []

        # Загрузка истории из файла
        self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Обновление отображения истории
        self.refresh_history_table()

    def create_widgets(self):
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, variable=self.password_length, orient="horizontal")
        self.length_scale.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)
        self.password_length.trace_add("write", lambda *args: self.length_label.configure(text=str(self.password_length.get())))

        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&* и др.)", variable=self.use_symbols).grid(row=1, column=2, sticky="w", pady=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле для отображения сгенерированного пароля
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        password_entry.pack(fill="x", padx=10, pady=5)

        # Кнопка копирования в буфер обмена
        copy_btn = ttk.Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)

        # Рамка для истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица истории (Treeview)
        columns = ("password", "length", "digits", "letters", "symbols", "timestamp")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("digits", text="Цифры")
        self.tree.heading("letters", text="Буквы")
        self.tree.heading("symbols", text="Спецсимволы")
        self.tree.heading("timestamp", text="Дата/время")

        self.tree.column("password", width=200)
        self.tree.column("length", width=60)
        self.tree.column("digits", width=70)
        self.tree.column("letters", width=70)
        self.tree.column("symbols", width=100)
        self.tree.column("timestamp", width=150)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить историю", command=self.save_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить историю", command=self.load_history).pack(side="left", padx=5)

    def generate_password(self):
        """Генерация пароля на основе выбранных параметров"""
        length = self.password_length.get()
        use_digits = self.use_digits.get()
        use_letters = self.use_letters.get()
        use_symbols = self.use_symbols.get()

        # Проверка, что выбран хотя бы один тип символов
        if not (use_digits or use_letters or use_symbols):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов (цифры, буквы или спецсимволы).")
            return

        # Проверка минимальной и максимальной длины (от 4 до 32)
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля — 4 символа.")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля — 32 символа.")
            return

        # Формируем пул символов
        chars = ""
        if use_digits:
            chars += string.digits
        if use_letters:
            chars += string.ascii_letters
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?/`~"

        # Гарантируем, что в пароле будут символы из каждого выбранного набора
        password_parts = []
        if use_digits:
            password_parts.append(random.choice(string.digits))
        if use_letters:
            password_parts.append(random.choice(string.ascii_letters))
        if use_symbols:
            password_parts.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?/`~"))

        # Добираем остальные символы
        remaining_length = length - len(password_parts)
        for _ in range(remaining_length):
            password_parts.append(random.choice(chars))

        # Перемешиваем, чтобы гарантированные символы не были только в начале
        random.shuffle(password_parts)
        password = "".join(password_parts)

        # Отображаем пароль
        self.password_var.set(password)

        # Добавляем в историю
        import time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "password": password,
            "length": length,
            "digits": use_digits,
            "letters": use_letters,
            "symbols": use_symbols,
            "timestamp": timestamp
        }
        self.history.append(entry)
        self.save_history()  # автоматически сохраняем при генерации
        self.refresh_history_table()

    def copy_to_clipboard(self):
        """Копирование текущего пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Информация", "Пароль скопирован в буфер обмена.")
        else:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль.")

    def refresh_history_table(self):
        """Обновление таблицы истории"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Заполняем заново
        for entry in reversed(self.history):  # новые сверху
            self.tree.insert("", "end", values=(
                entry["password"],
                entry["length"],
                "Да" if entry["digits"] else "Нет",
                "Да" if entry["letters"] else "Нет",
                "Да" if entry["symbols"] else "Нет",
                entry["timestamp"]
            ))

    def save_history(self):
        """Сохранение истории в JSON-файл"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        """Загрузка истории из JSON-файла"""
        if not os.path.exists(HISTORY_FILE):
            self.history = []
            return

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")
            self.history = []

    def clear_history(self):
        """Очистка истории (с подтверждением)"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()
            messagebox.showinfo("Информация", "История очищена.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
