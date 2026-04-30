import unittest
import json
import os
import tempfile
from datetime import datetime

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_temperature(temp_str):
    try:
        float(temp_str)
        return True
    except ValueError:
        return False


class TestWeatherDiary(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            {"date": "2026-01-15", "temperature": -5.0, "description": "Морозно", "precipitation": "нет"},
            {"date": "2026-01-16", "temperature": 0.0, "description": "Облачно", "precipitation": "да"},
            {"date": "2026-01-17", "temperature": 15.5, "description": "Солнечно", "precipitation": "нет"},
            {"date": "2026-01-18", "temperature": 22.0, "description": "Тепло", "precipitation": "нет"},
        ]

    def test_validate_date_positive(self):
        valid_dates = ["2026-01-15", "2026-12-31", "2027-02-28"]
        for date in valid_dates:
            self.assertTrue(validate_date(date), f"Дата {date} должна быть валидной")

    def test_validate_date_negative(self):
        invalid_dates = ["2026-13-01", "2026-01-32", "01-01-2026", "2026/01/15", "не дата"]
        for date in invalid_dates:
            self.assertFalse(validate_date(date), f"Дата {date} должна быть невалидной")

    def test_validate_temperature_positive(self):
        valid_temps = ["15", "15.5", "-5.0", "0", "22.5"]
        for temp in valid_temps:
            self.assertTrue(validate_temperature(temp), f"Температура {temp} должна быть валидной")

    def test_validate_temperature_negative(self):
        invalid_temps = ["пятнадцать", "15C", "15,5", "abc", ""]
        for temp in invalid_temps:
            self.assertFalse(validate_temperature(temp), f"Температура {temp} должна быть невалидной")

    def test_json_save_load(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_data, f, ensure_ascii=False, indent=4)

            with open(temp_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            self.assertEqual(len(loaded_data), len(self.test_data))
            for i in range(len(self.test_data)):
                self.assertEqual(loaded_data[i]["date"], self.test_data[i]["date"])
                self.assertEqual(loaded_data[i]["temperature"], self.test_data[i]["temperature"])
                self.assertEqual(loaded_data[i]["description"], self.test_data[i]["description"])
                self.assertEqual(loaded_data[i]["precipitation"], self.test_data[i]["precipitation"])
        finally:
            os.unlink(temp_file)

    def test_filter_by_date(self):
        filtered = [r for r in self.test_data if r["date"] == "2026-01-16"]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["temperature"], 0.0)

    def test_filter_by_temperature(self):
        threshold = 10.0
        filtered = [r for r in self.test_data if r["temperature"] > threshold]
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r["temperature"] > threshold for r in filtered))

    def test_boundary_temperature(self):
        self.assertTrue(validate_temperature("0"))
        self.assertTrue(validate_temperature("0.0"))
        self.assertTrue(validate_temperature("-0.0"))
        self.assertTrue(validate_temperature("-100"))
        self.assertTrue(validate_temperature("100"))
        self.assertTrue(validate_temperature("999.999"))

    def test_data_structure(self):
        for record in self.test_data:
            self.assertIn("date", record)
            self.assertIn("temperature", record)
            self.assertIn("description", record)
            self.assertIn("precipitation", record)
            self.assertIsInstance(record["date"], str)
            self.assertIsInstance(record["temperature"], (int, float))
            self.assertIsInstance(record["description"], str)
            self.assertIn(record["precipitation"], ["да", "нет"])


if __name__ == "__main__":
    unittest.main()
