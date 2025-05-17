import pandas as pd
import numpy as np
import json

# 1. بارگذاری دیتافریم
file_path = './datasets/text_corrected_data.parquet'
df = pd.read_parquet(file_path)

# 2. فقط ستون‌های عددی
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# 3. دیکشنری برای ذخیره پارامترهای نرمال‌سازی
normalization_params = {}
scaling_method = 'minmax'  # یا 'zscore'

# 4. نرمال‌سازی
df_scaled = df.copy()
for col in numerical_cols:
    values = df[col].values

    if scaling_method == 'minmax':
        min_val = float(values.min())
        max_val = float(values.max())
        scaled = (values - min_val) / (max_val - min_val)
        df_scaled[col] = scaled

        normalization_params[col] = {
            "method": "minmax",
            "min": min_val,
            "max": max_val
        }

    elif scaling_method == 'zscore':
        mean_val = float(values.mean())
        std_val = float(values.std())
        scaled = (values - mean_val) / std_val
        df_scaled[col] = scaled

        normalization_params[col] = {
            "method": "zscore",
            "mean": mean_val,
            "std": std_val
        }

# 5. ذخیره دیتافریم نرمال‌شده
scaled_output_path = './datasets/normalize_data.parquet'
df_scaled.to_parquet(scaled_output_path)

# 6. تبدیل مقادیر float32/float64 به float برای ذخیره در JSON
def convert_to_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(v) for v in obj]
    elif isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
        return float(obj)
    else:
        return obj

params_output_path = './datasets/normalization_params.json'
with open(params_output_path, 'w') as f:
    json.dump(convert_to_json_serializable(normalization_params), f, indent=4)

print(f"\n✅ نرمال‌سازی کامل شد و فایل‌ها ذخیره شدند:")
print(f"📦 داده نرمال‌شده: {scaled_output_path}")
print(f"🧾 پارامترهای نرمال‌سازی: {params_output_path}")
