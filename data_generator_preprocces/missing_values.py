import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

# 1. بارگذاری داده و کپی گرفتن
file_path = './datasets/text_corrected_data.parquet'
df = pd.read_parquet(file_path)
df_original = df.copy()

# 2. ستون‌های دارای مقدار گمشده
missing_report = df.isnull().sum()
missing_report = missing_report[missing_report > 0]
print("ستون‌هایی با مقادیر گمشده:")
print(missing_report)

# فقط ستون‌های عددی را انتخاب کن (float و int کلی)
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()

imputation_report = []

# 3. ایمپوت با CatBoost
for col in missing_report.index:
    if col not in numerical_cols:
        continue

    print(f"\n🏗 در حال ایمپوتر کردن ستون: {col}")

    train_data = df[df[col].notnull()]
    test_data = df[df[col].isnull()]

    if train_data.shape[0] < 50 or test_data.shape[0] == 0:
        print(f"⛔ داده کافی برای آموزش CatBoost برای {col} وجود ندارد.")
        continue

    # انتخاب ویژگی‌ها به جز ستون هدف
    features_for_model = [c for c in numerical_cols if c != col]

    X_train = train_data[features_for_model].dropna(axis=1)
    y_train = train_data[col]
    X_test = test_data[X_train.columns]

    # تقسیم داده برای اعتبارسنجی ساده
    X_train_part, X_val, y_train_part, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )

    # مدل CatBoost
    model = CatBoostRegressor(
        iterations=500,
        learning_rate=0.01,
        depth=6,
        loss_function='MAE',
        verbose=False,
        random_seed=42
    )

    model.fit(X_train_part, y_train_part, eval_set=(X_val, y_val), early_stopping_rounds=50)

    # پیش‌بینی مقدارهای گمشده
    y_pred_missing = model.predict(X_test)
    df.loc[df[col].isnull(), col] = y_pred_missing

    # ارزیابی مدل روی داده اعتبارسنجی
    y_val_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, y_val_pred)
    mean_val = np.mean(y_val)
    percent_error = (mae / mean_val) * 100

    imputation_report.append({
        "ستون": col,
        "MAE": mae,
        "میانگین مقدار واقعی": mean_val,
        "درصد خطا": round(percent_error, 2)
    })

# 4. گزارش نهایی
print("\n📝 گزارش تخمین مقادیر گمشده با CatBoost:")
report_df = pd.DataFrame(imputation_report)
print(report_df)

# 5. ذخیره دیتافریم اصلاح شده در فایل جدید
output_file = './datasets/cleaned_without_missing.parquet'  # می‌تونی .csv هم بزاری اگر خواستی
df.to_parquet(output_file, index=False)
print(f"\n✅ فایل با مقادیر ایمپوت شده در '{output_file}' ذخیره شد.")
