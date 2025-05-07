import pandas as pd
import json
from typing import Dict, Any

class QualityChecker:
    def __init__(self):
        self.report = {}

    def generate_report(self, df) -> Dict[str, Any]:
        """تولید گزارش جامع کیفیت داده‌ها"""
        self._check_missing_values(df)
        self._check_value_ranges(df)
        self._check_data_distribution(df)
        return self.report

    def _check_missing_values(self, df):
        """بررسی مقادیر گم‌شده"""
        self.report['missing_values'] = {
            'total': df.isnull().sum().sum(),
            'by_column': df.isnull().sum().to_dict()
        }

    def _check_value_ranges(self, df):
        """بررسی محدوده‌های منطقی برای مقادیر"""
        ranges = {
            'Temperature_C': (0, 400),
            'Pressure_psi': (0, 30000),
            'pH': (0, 14)
        }
        violations = {}
        for col, (min_val, max_val) in ranges.items():
            if col in df.columns:
                violations[col] = {
                    'below_min': (df[col] < min_val).sum(),
                    'above_max': (df[col] > max_val).sum()
                }
        self.report['value_range_violations'] = violations

    def save_report(self, file_path: str):
        """ذخیره گزارش در فایل"""
        with open(file_path, 'w') as f:
            json.dump(self.report, f, indent=4)