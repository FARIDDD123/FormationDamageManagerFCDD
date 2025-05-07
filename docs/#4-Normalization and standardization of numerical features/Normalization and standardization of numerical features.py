import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pickle
import json

# بارگذاری داده‌های پیش‌پردازش شده
df = pd.read_parquet("/content/formation_damage_imputed.parquet")

# شناسایی ستون‌های عددی
numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns

# 1. نرمال‌سازی و استانداردسازی ستون‌های عددی
def normalize_data(df, numerical_cols, strategy='minmax'):
    """
    نرمال‌سازی یا استانداردسازی ستون‌های عددی
    
    پارامترها:
    df -- دیتافریم ورودی
    numerical_cols -- لیست ستون‌های عددی
    strategy -- استراتژی نرمال‌سازی ('minmax' یا 'zscore')
    
    برمی‌گرداند:
    دیتافریم نرمال‌سازی شده، پارامترهای نرمال‌سازی
    """
    
    normalized_df = df.copy()
    normalization_params = {}
    
    for col in numerical_cols:
        if strategy == 'minmax':
            scaler = MinMaxScaler()
            normalized_df[col] = scaler.fit_transform(normalized_df[[col]])
            # ذخیره پارامترها
            normalization_params[col] = {
                'type': 'minmax',
                'min': scaler.data_min_[0],
                'max': scaler.data_max_[0]
            }
        elif strategy == 'zscore':
            scaler = StandardScaler()
            normalized_df[col] = scaler.fit_transform(normalized_df[[col]])
            # ذخیره پارامترها
            normalization_params[col] = {
                'type': 'zscore',
                'mean': scaler.mean_[0],
                'std': scaler.scale_[0]
            }
    
    return normalized_df, normalization_params

# اعمال نرمال‌سازی (می‌توانید strategy را به 'zscore' تغییر دهید)
normalized_df, normalization_params = normalize_data(df, numerical_cols, strategy='minmax')

# 2. ذخیره پارامترهای نرمال‌سازی برای استفاده در فاز پیش‌بینی
def save_normalization_params(params, file_path):
    """
    ذخیره پارامترهای نرمال‌سازی در فایل
    
    پارامترها:
    params -- دیکشنری پارامترهای نرمال‌سازی
    file_path -- مسیر فایل خروجی
    """
    with open(file_path, 'wb') as f:
        pickle.dump(params, f)

save_normalization_params(normalization_params, 'normalization_params.pkl')

# 3. مستندسازی نحوه اعمال نرمال‌سازی برای هر ستون
def generate_normalization_documentation(params):
    """
    تولید مستندات نرمال‌سازی
    
    پارامترها:
    params -- دیکشنری پارامترهای نرمال‌سازی
    
    برمی‌گرداند:
    رشته مستندات
    """
    docs = "مستندات نرمال‌سازی ویژگی‌های عددی:\n\n"
    docs += "="*50 + "\n"
    
    for col, param in params.items():
        docs += f"ستون: {col}\n"
        docs += f"نوع نرمال‌سازی: {param['type']}\n"
        
        if param['type'] == 'minmax':
            docs += f"مقدار حداقل اصلی: {param['min']:.4f}\n"
            docs += f"مقدار حداکثر اصلی: {param['max']:.4f}\n"
            docs += "فرمول اعمال شده: (مقدار - min) / (max - min)\n"
        elif param['type'] == 'zscore':
            docs += f"میانگین اصلی: {param['mean']:.4f}\n"
            docs += f"انحراف معیار اصلی: {param['std']:.4f}\n"
            docs += "فرمول اعمال شده: (مقدار - mean) / std\n"
        
        docs += "-"*50 + "\n"
    
    return docs

# تولید و ذخیره مستندات
normalization_docs = generate_normalization_documentation(normalization_params)
with open('normalization_documentation.txt', 'w', encoding='utf-8') as f:
    f.write(normalization_docs)

# ذخیره داده‌های نرمال‌سازی شده
normalized_df.to_parquet("formation_damage_normalized.parquet", index=False)

print("\n" + "="*50)
print("[SUCCESS] Normalization completed successfully!")
print(f"- Normalized data saved to 'formation_damage_normalized.parquet'")
print(f"- Normalization parameters saved to 'normalization_params.pkl'")
print(f"- Normalization documentation saved to 'normalization_documentation.txt'")
print("="*50 + "\n")

# نمایش نمونه‌ای از مستندات
print(normalization_docs.split("="*50)[0] + "..." + "\n(مستندات کامل در فایل ذخیره شده است)")