"""
Weather Diary - Дневник погоды
Графическое приложение для ведения записей о погоде с сохранением в JSON.

Автор: Хайбуллин Радмир Рамилевич
Версия: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Путь к файлу для хранения данных
DATA_FILE = "data.json"


class WeatherDiaryApp:
    """
    Основной класс приложения Weather Diary.
    Управляет интерфейсом, данными и логикой работы.
    """

    def __init__(self, root):
        """
        Инициализация приложения.
        
        Args:
            root: Корневое окно tkinter
        """
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")

        # Список записей о погоде
        self.records = []
        # Загрузка сохраненных данных
        self.load_data()

        # Создание интерфейса
        self.create_widgets()
        # Обновление таблицы
        self.update_table()

    def create_widgets(self):
        """Создание всех элементов интерфейса приложения."""
        # Фрейм для ввода новой записи
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поле ввода даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)

        # Поле ввода температуры
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=2)

        # Поле ввода описания
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2)

        # Поле выбора осадков
        ttk.Label(input_frame, text="Осадки:").grid(row=1, column=3, sticky="w")
        self.precipitation_var = tk.StringVar(value="нет")
        self.precipitation_combo = ttk.Combobox(input_frame, textvariable=self.precipitation_var,
                                                  values=["да", "нет"], width=8, state="readonly")
        self.precipitation_combo.grid(row=1, column=4, padx=5, pady=2)

        # Кнопка добавления записи
        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(
            row=0, column=4, rowspan=2, padx=10)

        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Поле фильтра по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=2)

        # Поле фильтра по температуре
        ttk.Label(filter_frame, text="Фильтр по температуре (>):").grid(row=0, column=2, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=2)

        # Кнопки фильтрации
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(
            row=0, column=5, padx=5)

        # Таблица для отображения записей
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка заголовков колонок
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        # Настройка ширины колонок
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Фрейм для кнопок управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранную", command=self.delete_record).pack(side="left", padx=5)

    def validate_date(self, date_str):
        """
        Валидация формата даты.
        
        Args:
            date_str: Строка с датой для проверки
            
        Returns:
            bool: True если дата валидна, False иначе
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_temperature(self, temp_str):
        """
        Валидация значения температуры.
        
        Args:
            temp_str: Строка с температурой для проверки
            
        Returns:
            bool: True если температура валидна (число), False иначе
        """
        try:
            float(temp_str)
            return True
        except ValueError:
            return False

    def add_record(self):
        """Добавление новой записи о погоде с валидацией данных."""
        # Получение данных из полей ввода
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precipitation_var.get()

        # Валидация даты
        if not date:
            messagebox.showerror("Ошибка", "Введите дату!")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        # Валидация температуры
        if not temp:
            messagebox.showerror("Ошибка", "Введите температуру!")
            return
        if not self.validate_temperature(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return

        # Валидация описания
        if not description:
            messagebox.showerror("Ошибка", "Введите описание погоды!")
            return

        # Создание записи
        record = {
            "date": date,
            "temperature": float(temp),
            "description": description,
            "precipitation": precipitation
        }
        
        # Добавление в список и сохранение
        self.records.append(record)
        self.save_data()
        self.update_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена!")

    def delete_record(self):
        """Удаление выбранной записи из таблицы."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return

        # Удаление выбранных записей из списка
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
        """Применение фильтра по дате и/или температуре."""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()

        filtered = self.records.copy()

        # Фильтрация по дате
        if filter_date:
            if self.validate_date(filter_date):
                filtered = [r for r in filtered if r["date"] == filter_date]
            else:
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра!")
                return

        # Фильтрация по температуре
        if filter_temp:
            if self.validate_temperature(filter_temp):
                temp_threshold = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            else:
                messagebox.showerror("Ошибка", "Неверный формат температуры фильтра!")
                return

        self.update_table(filtered)

    def reset_filter(self):
        """Сброс всех фильтров."""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()

    def update_table(self, records=None):
        """
        Обновление таблицы с записями.
        
        Args:
            records: Список записей для отображения (если None, используются все записи)
        """
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Отображение записей
        display_records = records if records is not None else self.records

        for record in display_records:
            self.tree.insert("", "end", values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))

    def clear_inputs(self):
        """Очистка всех полей ввода."""
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set("нет")

    def save_data(self):
        """Сохранение всех записей в JSON файл."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузка записей из JSON файла."""
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
    """Точка входа в приложение."""
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
