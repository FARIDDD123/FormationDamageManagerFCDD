import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_score

# 1. بارگذاری و پیش‌پردازش داده‌ها
df = pd.read_parquet("formation_damage_valid_data.parquet")

# کد موجود برای حذف ترکیبات نامعتبر
cond1 = (df['Formation'] == 'Shale') & (df['Fluid_Type'] == 'Acidic') & (df['Completion_Type'] == 'Open Hole')
cond2 = (df['Formation'] == 'Carbonate') & (df['Fluid_Type'] == 'Brine') & (df['Completion_Type'] == 'Open Hole')
cond3 = (df['Formation'] == 'Sandstone') & (df['Fluid_Type'] == 'Water-Based') & (df['Completion_Type'] == 'Perforated')
cond4 = (df['Formation'] == 'Shale') & (df['Fluid_Type'] == 'Oil-Based') & (df['Completion_Type'] == 'Perforated')

df['Invalid_Combination'] = cond1 | cond2 | cond3 | cond4

invalid_percentage = df['Invalid_Combination'].sum() / len(df) * 100

if invalid_percentage < 1:
    df_cleaned = df.drop(columns=["Invalid_Combination"])
elif 1 <= invalid_percentage < 5:
    df_cleaned = df[~df['Invalid_Combination']].drop(columns=["Invalid_Combination"])
else:
    df_cleaned = df.drop(columns=["Invalid_Combination"])

# 2. تحلیل مقادیر گمشده
print("\n" + "="*50 + "\nMissing Values Analysis:")
missing_data = df_cleaned.isnull().sum()
missing_percentage = (missing_data / len(df_cleaned)) * 100
missing_report = pd.DataFrame({
    'Missing Values': missing_data,
    'Percentage (%)': missing_percentage.round(2)
}).sort_values(by='Missing Values', ascending=False)
print(missing_report[missing_report['Missing Values'] > 0])

# 3. مدیریت مقادیر گمشده
# الف) شناسایی خودکار ستون‌های عددی دارای مقادیر گمشده
numerical_cols = df_cleaned.select_dtypes(include=['float64', 'int64']).columns
numerical_cols_with_missing = numerical_cols[df_cleaned[numerical_cols].isnull().any()]

if len(numerical_cols_with_missing) > 0:
    print(f"\nImputing numerical columns: {list(numerical_cols_with_missing)}")
    imputer = KNNImputer(n_neighbors=5)
    df_cleaned[numerical_cols_with_missing] = imputer.fit_transform(df_cleaned[numerical_cols_with_missing])
    
    # ارزیابی دقت KNN (فقط اگر داده کافی وجود دارد)
    if len(df_cleaned) > 100:
        sample = df_cleaned[numerical_cols_with_missing].dropna().sample(100, random_state=42)
        if len(sample) > 0:
            original_values = sample.copy()
            sample.iloc[::10] = np.nan
            imputed_sample = imputer.transform(sample)
            mae = mean_absolute_error(original_values, imputed_sample)
            print(f"KNN Imputer Evaluation - MAE: {mae:.4f}")

# ب) شناسایی خودکار ستون‌های دسته‌بندی دارای مقادیر گمشده
categorical_cols = df_cleaned.select_dtypes(include=['object', 'category']).columns
categorical_cols_with_missing = categorical_cols[df_cleaned[categorical_cols].isnull().any()]

for col in categorical_cols_with_missing:
    print(f"\nImputing categorical column: {col}")
    
    # یک‌هوت کدگذاری برای تمام ستون‌های دسته‌بندی
    df_encoded = pd.get_dummies(df_cleaned, columns=df_cleaned.select_dtypes(include=['object', 'category']).columns.drop(col))
    
    # تقسیم داده‌ها
    known_data = df_encoded.dropna(subset=[col])
    unknown_data = df_encoded[df_encoded[col].isnull()]
    
    if len(unknown_data) > 0 and len(known_data) > 0:
        X_train = known_data.drop(col, axis=1)
        y_train = known_data[col]
        
        try:
            # ارزیابی مدل با اعتبارسنجی متقاطع
            model = LogisticRegression(max_iter=1000, random_state=42)
            scores = cross_val_score(model, X_train, y_train, cv=min(5, len(known_data)), scoring='accuracy')
            print(f"Logistic Regression CV Accuracy: {np.mean(scores):.2%} (±{np.std(scores):.2%})")
            
            # آموزش و پیش‌بینی نهایی
            model.fit(X_train, y_train)
            predictions = model.predict(unknown_data.drop(col, axis=1))
            df_cleaned.loc[unknown_data.index, col] = predictions
        except Exception as e:
            print(f"Could not impute {col} using Logistic Regression. Using mode instead. Error: {str(e)}")
            df_cleaned[col].fillna(df_cleaned[col].mode()[0], inplace=True)

# 4. ذخیره‌سازی داده نهایی
df_cleaned.to_parquet("formation_damage_imputed.parquet", index=False)
print("\n" + "="*50 + "\n[SUCCESS] Imputed data saved to 'formation_damage_imputed.parquet'")