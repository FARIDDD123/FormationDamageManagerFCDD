
# tests/integration/test_full_pipeline.py
import sys
sys.path.append('/Users/parnian/Desktop/oil_well_analytics/drilling_data_processor')

from drilling_data_processor.drilling_processor.core import DrillingDataProcessor


from pathlib import Path

def test_processing_pipeline(tmp_path, sample_well_data):
    """تست کامل پایتلاین پردازش داده‌های حفاری"""
    # 1. ذخیره داده تست
    test_file = tmp_path / "test_wells.parquet"
    sample_well_data.to_parquet(test_file)
    
    # 2. اجرای پایتلاین
    processor = DrillingDataProcessor(test_file)
    processed = processor.run_pipeline()
    
    # 3. Assertهای اصلی
    assert not processed.empty
    assert 'PT_Ratio' in processed.columns  # بررسی feature engineering
    assert processed.isna().sum().sum() == 0  # بررسی عدم وجود مقادیر گم‌شده