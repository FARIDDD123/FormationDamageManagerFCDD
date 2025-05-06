1. وارد کردن کتابخانهها
python
import pandas as pd
از کتابخانه pandas برای مدیریت دادهها استفاده میشود.

2. بارگذاری دادهها
python
df = pd.read_parquet("/content/drive/MyDrive/Colab Notebooks/formation_damage_cleaned/formation_damage_cleaned.parquet")
دادهها از یک فایل Parquet در مسیر مشخص بارگذاری میشوند. این فایل احتمالاً حاوی دادههای پاکسازی شده اولیه است.

3. تعریف ترکیبات نامعتبر
چهار شرط برای ترکیبات نامعتبر تعریف شده است:

python
cond1 = (df['Formation'] == 'Shale') & (df['Fluid_Type'] == 'Acidic') & (df['Completion_Type'] == 'Open Hole')
cond2 = (df['Formation'] == 'Carbonate') & (df['Fluid_Type'] == 'Brine') & (df['Completion_Type'] == 'Open Hole')
cond3 = (df['Formation'] == 'Sandstone') & (df['Fluid_Type'] == 'Water-Based') & (df['Completion_Type'] == 'Perforated')
cond4 = (df['Formation'] == 'Shale') & (df['Fluid_Type'] == 'Oil-Based') & (df['Completion_Type'] == 'Perforated')
شرایط بر اساس دانش دامنه (مثلاً ترکیباتی که باعث آسیب به سازند میشوند) تنظیم شدهاند.

هر شرط ترکیبی خاص از Formation، Fluid_Type، و Completion_Type را بررسی میکند.

4. افزودن ستون ترکیبات نامعتبر
python
df['Invalid_Combination'] = cond1 | cond2 | cond3 | cond4
یک ستون جدید Invalid_Combination ایجاد میشود که True/False را نشان میدهد.

5. محاسبه درصد دادههای نامعتبر
python
invalid_count = df['Invalid_Combination'].sum()
invalid_percentage = invalid_count / len(df) * 100
print(f"Percentage of invalid combinations: {invalid_percentage:.2f}%")
تعداد و درصد ردیفهای نامعتبر محاسبه و چاپ میشود.

6. تصمیمگیری بر اساس درصد نامعتبرها
الف. کمتر از ۱% نامعتبر
python
if invalid_percentage < 1:
    print("Invalid combinations are less than 1%, ignoring the issue.")
    df_cleaned = df.drop(columns=["Invalid_Combination"])
اگر نامعتبرها ناچیز باشند، فقط ستون Invalid_Combination حذف میشود.

ب. ۱% تا ۵% نامعتبر
python
elif 1 <= invalid_percentage < 5:
    print("Invalid combinations are between 1% and 5%, removing invalid rows.")
    df_cleaned = df[~df['Invalid_Combination']].drop(columns=["Invalid_Combination"])
    print(f"Removed {invalid_count} invalid rows.")
ردیفهای نامعتبر حذف شده و ستون Invalid_Combination حذف میشود.

ج. ۵% تا ۱۰% نامعتبر
python
elif 5 <= invalid_percentage < 10:
    print("Invalid combinations are between 5% and 10%, further investigation recommended.")
    df[df['Invalid_Combination']].to_csv("invalid_rows.csv", index=False)
    print("[INFO] Invalid rows saved for further investigation.")
    df_cleaned = df.drop(columns=["Invalid_Combination"])
ردیفهای نامعتبر در فایل invalid_rows.csv ذخیره شده و نیاز به بررسی بیشتر دارند.

د. بیش از ۱۰% نامعتبر
python
else:
    print("Invalid combinations are more than 10%, reconsider data collection process.")
    df[df['Invalid_Combination']].to_csv("invalid_rows.csv", index=False)
    print("[WARNING] Large number of invalid rows saved for auditing.")
    df_cleaned = df.drop(columns=["Invalid_Combination"])
هشدار داده میشود و ردیفهای نامعتبر برای ممیزی ذخیره میشوند.

7. ذخیره دادههای پاکسازی شده
python
df_cleaned.to_parquet("formation_damage_valid_data.parquet", index=False)
print("[SUCCESS] Cleaned data saved to 'formation_damage_valid_data.parquet'")
دادههای نهایی بدون ستون Invalid_Combination در قالب Parquet ذخیره میشوند.

