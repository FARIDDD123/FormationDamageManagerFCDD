import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

file_path = './datasets/text_corrected_data.parquet'  # نام فایل ورودی
df = pd.read_parquet(file_path)

columns_to_check = ['Temperature_C', 'Pressure_psi', 'Permeability_mD', 'Flow_Rate_bbl_day']  # به دلخواه تغییر بده

# روش IQR
def detect_outliers_iqr(df, columns):
    outliers = pd.DataFrame()
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_rows = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outliers = pd.concat([outliers, outlier_rows])
    return outliers.drop_duplicates()

# روش Z-Score
def detect_outliers_zscore(df, columns, threshold=3):
    z_scores = np.abs(zscore(df[columns]))
    outliers = df[(z_scores > threshold).any(axis=1)]
    return outliers.drop_duplicates()

# شناسایی داده‌های پرت
iqr_outliers = detect_outliers_iqr(df, columns_to_check)
zscore_outliers = detect_outliers_zscore(df, columns_to_check)

# ادغام نتایج بدون تکرار
all_outliers = pd.concat([iqr_outliers, zscore_outliers]).drop_duplicates()

# آمار
total_rows = len(df)
iqr_count = len(iqr_outliers)
zscore_count = len(zscore_outliers)
combined_count = len(all_outliers)

print("📊 آمار داده‌های پرت شناسایی‌شده:")
print(f"- با روش IQR: {iqr_count} ({iqr_count / total_rows:.2%})")
print(f"- با روش Z-Score: {zscore_count} ({zscore_count / total_rows:.2%})")
print(f"- مجموع بدون تکرار: {combined_count} ({combined_count / total_rows:.2%})")

# ذخیره داده‌های پرت در فایل
cleaned_file = './datasets/outliers.parquet'
all_outliers.to_parquet(cleaned_file, index=False)
print(f"✅ داده‌های پرت در فایل '{cleaned_file}' ذخیره شدند.")
