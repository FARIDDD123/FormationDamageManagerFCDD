import pandas as pd
import numpy as np

file_path = './datasets/text_corrected_data.parquet'  # نام فایل ورودی
df = pd.read_parquet(file_path)

invalid_combinations = [
    ("shale", "acid", "open hole"),
    ("shale", "oil-based", "open hole"),
    ("shale", "acid", "perforated"),
    ("shale", "brine", "open hole"),
    ("carbonate", "oil-based", "liner"), #it can be wrong
    ("mixed", "acid", "open hole"),
    ("mixed", "oil-based", "open hole"),
    ("sandstone", "acid", "open hole"),
    ("sandstone", "brine", "open hole"),
    ("dolomite", "water-based", "open hole"),
]

invalid_set = set(invalid_combinations)

# فیلتر داده‌های نامعتبر
invalid_df = df[df.apply(lambda row: (row['Formation'], row['Fluid_Type'], row['Completion_Type']) in invalid_set, axis=1)]

# حذف داده‌های نامعتبر از دیتاست اصلی
df_cleaned = df.drop(invalid_df.index).reset_index(drop=True)

# محاسبه درصد داده‌های حذف شده
percent_invalid = 100 * len(invalid_df) / len(df)

print(f"تعداد داده‌های حذف شده: {len(invalid_df)}")
print(f"درصد داده‌های حذف شده نسبت به کل دیتاست: {percent_invalid:.2f}%")

cleaned_file = './datasets/invalid_combinations.parquet'
invalid_df.to_parquet(cleaned_file, index=False)
print(f"✅ داده‌های پاک‌شده در فایل '{cleaned_file}' ذخیره شدند.")
