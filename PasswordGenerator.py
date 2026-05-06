import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# --- Настройки ---
API_URL = "https://api.exchangerate-api.com/v4/latest/"
HISTORY_FILE = "history.json"

# --- Функции ---

def load_history():
    """Загружает историю из файла JSON."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(entry):
    """Сохраняет новую запись в историю."""
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def update_history_table():
    """Обновляет таблицу истории в GUI."""
    for i in history_tree.get_children():
        history_tree.delete(i)
    for item in load_history():
        history_tree.insert("", "end", values=(
            item["from"],
            item["to"],
            f"{item['amount']:.2f}",
            f"{item['result']:.2f}"
        ))

def is_valid_amount(value):
    """Проверяет, что введённое значение — положительное число."""
    try:
        amount = float(value)
        return amount > 0
    except ValueError:
        return False

def get_exchange_rate(base_currency, target_currency):
    """Запрашивает курс обмена у внешнего API."""
    try:
        response = requests.get(f"{API_URL}{base_currency}")
        response.raise_for_status()
        data = response.json()
        return data["rates"][target_currency]
    except (requests.RequestException, KeyError) as e:
        messagebox.showerror("Ошибка API", f"Не удалось получить курс валют: {e}")
        return None

def convert_currency():
    """Основная функция конвертации."""
    from_cur = from_currency.get()
    to_cur = to_currency.get()
    amount_str = amount_entry.get()

    if not is_valid_amount(amount_str):
        messagebox.showerror("Ошибка ввода", "Пожалуйста, введите положительное число в поле суммы.")
        return

    amount = float(amount_str)
    rate = get_exchange_rate(from_cur, to_cur)

    if rate is not None:
        result = amount * rate
        result_label.config(text=f"Результат: {result:.2f} {to_cur}")

        # Сохраняем в историю
        save_history({
            "from": from_cur,
            "to": to_cur,
            "amount": amount,
            "result": result,
            "rate": rate
        })
        update_history_table()

# --- Создание GUI ---

root = tk.Tk()
root.title("Currency Converter")
root.geometry("600x400")

# Валюты (можно расширить список)
CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]

# Элементы интерфейса
tk.Label(root, text="Из:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="В:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Сумма:").grid(row=2, column=0, padx=10, pady=5, sticky="e")

from_currency = ttk.Combobox(root, values=CURRENCIES)
to_currency = ttk.Combobox(root, values=CURRENCIES)
amount_entry = tk.Entry(root)

from_currency.current(0)  # USD по умолчанию
to_currency.current(1)     # EUR по умолчанию

from_currency.grid(row=0, column=1, padx=10, pady=5)
to_currency.grid(row=1, column=1, padx=10, pady=5)
amount_entry.grid(row=2, column=1, padx=10, pady=5)

convert_button = tk.Button(root, text="Конвертировать", command=convert_currency)
convert_button.grid(row=3, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="Результат: ", font=("Arial", 12))
result_label.grid(row=4, column=0, columnspan=2, pady=5)

# Таблица истории
history_tree = ttk.Treeview(root, columns=("from", "to", "amount", "result"), show="headings")
history_tree.heading("from", text="Из")
history_tree.heading("to", text="В")
history_tree.heading("amount", text="Сумма")
history_tree.heading("result", text="Результат")
history_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Загрузка истории при старте
update_history_table()

# Настройка размеров сетки
root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
