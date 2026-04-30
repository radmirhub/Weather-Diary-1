import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data.json"


class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")

        self.records = []
        self.load_data()

        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2)

        ttk.Label(input_frame, text="Осадки:").grid(row=1, column=3, sticky="w")
        self.precipitation_var = tk.StringVar(value="нет")
        self.precipitation_combo = ttk.Combobox(input_frame, textvariable=self.precipitation_var,
                                                  values=["да", "нет"], width=8, state="readonly")
        self.precipitation_combo.grid(row=1, column=4, padx=5, pady=2)

        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(
            row=0, column=4, rowspan=2, padx=10)

        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Фильтр по температуре (>):").grid(row=0, column=2, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(
            row=0, column=5, padx=5)

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранную", command=self.delete_record).pack(side="left", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_temperature(self, temp_str):
        try:
            float(temp_str)
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precipitation_var.get()

        if not date:
            messagebox.showerror("Ошибка", "Введите дату!")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        if not temp:
            messagebox.showerror("Ошибка", "Введите температуру!")
            return
        if not self.validate_temperature(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return

        if not description:
            messagebox.showerror("Ошибка", "Введите описание погоды!")
            return

        record = {
            "date": date,
            "temperature": float(temp),
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        self.save_data()
        self.update_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена!")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return

        for item in selected:
            values = self.tree.item(item, "values")
            self.records = [r for r in self.records
                           if not (r["date"] == values[0] and
                                   str(r["temperature"]) == values[1] and
                                   r["description"] == values[2])]

        self.save_data()
        self.update_table()
        messagebox.showinfo("Успех", "Запись удалена!")

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()

        filtered = self.records.copy()

        if filter_date:
            if self.validate_date(filter_date):
                filtered = [r for r in filtered if r["date"] == filter_date]
            else:
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра!")
                return

        if filter_temp:
            if self.validate_temperature(filter_temp):
                temp_threshold = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            else:
                messagebox.showerror("Ошибка", "Неверный формат температуры фильтра!")
                return

        self.update_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()

    def update_table(self, records=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_records = records if records is not None else self.records

        for record in display_records:
            self.tree.insert("", "end", values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set("нет")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            else:
                self.records = []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            self.records = []


def main():
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
