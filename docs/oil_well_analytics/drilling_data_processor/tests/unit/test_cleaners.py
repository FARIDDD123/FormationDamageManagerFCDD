import sys
import pytest
import pandas as pd
from drilling_data_processor.drilling_processor.preprocessors.cleaners import DataCleaner

sys.path.append('/Users/parnian/Desktop/oil_well_analytics/drilling_data_processor')

@pytest.fixture
def sample_well_data():
    """نمونه داده تستی با مقادیر NaN برای بررسی ایمپوت"""
    return pd.DataFrame({
        'Well_ID': ['WELL_001', 'WELL_002', 'WELL_003'],
        'Temperature_C': [80.5, 120.3, None],  # مقدار NaN برای تست ایمپوت عددی
        'Pressure_psi': [5000, 12000, 8000],
        'Formation': ['Sandstone', 'Carbonate', None],  # مقدار NaN برای تست ایمپوت متنی
        'Damage_Type': ['Clay & Iron', None, 'Fluid Loss']  # مقدار NaN برای تست ایمپوت متنی
    })

def test_cleaner_imputation(sample_well_data):
    """تست عملکرد imputer بر روی داده‌های حفاری"""
    cleaner = DataCleaner()
    
    # ✅ اعمال ایمپوت سفارشی برای ستون‌های متنی
    cleaned = cleaner.handle_missing_values(
        sample_well_data,
        custom_strategy={"Formation": "most_frequent", "Damage_Type": "most_frequent"}
    )
    
    # ✅ بررسی اینکه هیچ مقدار NaN باقی نمانده
    assert cleaned.isna().sum().sum() == 0, f"❌ مقدار NaN باقی مانده: \n{cleaned.isna().sum()}"

    # ✅ بررسی حفظ ساختار داده‌ها
    assert set(cleaned.columns) == set(sample_well_data.columns), "❌ نام ستون‌ها تغییر کرده!"
