import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal, beta
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 1. تولید داده‌های همبسته فیزیکی --------------------------------------------------------
def generate_core_data(normal_samples=10_000_000, abnormal_samples=500_000):
    # تنظیمات همبستگی بر اساس فیزیک سازند
    corr_matrix = np.array([
        [1.0, 0.85, -0.9, 0.7, 0.6],    # فشار
        [0.85, 1.0, -0.8, 0.6, 0.5],    # دما
        [-0.9, -0.8, 1.0, -0.7, -0.6],  # نفوذپذیری
        [0.7, 0.6, -0.7, 1.0, 0.8],     # رس
        [0.6, 0.5, -0.6, 0.8, 1.0]      # شوری
    ])
    
    # تولید داده‌های پایه
    mv = multivariate_normal(mean=[0]*5, cov=corr_matrix, allow_singular=True)
    data = mv.rvs(normal_samples + abnormal_samples)
    
    # تبدیل به مقادیر واقعی
    df = pd.DataFrame(data, columns=['pressure', 'temp', 'perm', 'clay', 'salinity'])
    
    # نگاشت مقادیر
    df['pressure'] = 2000 + (13000 * (df['pressure'] - df['pressure'].min()) / (df['pressure'].max() - df['pressure'].min())
    df['temp'] = 50 + (200 * (df['temp'] - df['temp'].min()) / (df['temp'].max() - df['temp'].min())
    df['perm'] = 0.001 + (100 * (df['perm'] - df['perm'].min()) / (df['perm'].max() - df['perm'].min()))
    df['clay'] = 5 + 35 * (df['clay'] - df['clay'].min()) / (df['clay'].max() - df['clay'].min())
    df['salinity'] = 10000 + (240000 * (df['salinity'] - df['salinity'].min()) / (df['salinity'].max() - df['salinity'].min()))
    
    return df

# 2. تزریق داده‌های غیرعملی (نان پرکتیکال) -----------------------------------------------
def add_nonpractical_data(df, num_anomalies=50_000):
    # ایجاد داده‌های فیزیکی غیرممکن اما معنادار
    nonpractical = pd.DataFrame({
        'pressure': np.random.uniform(18000, 25000, num_anomalies),
        'temp': np.random.uniform(300, 500, num_anomalies),
        'perm': np.random.uniform(-0.5, -0.001, num_anomalies), # نفوذپذیری منفی!
        'clay': np.random.uniform(45, 70, num_anomalies),
        'salinity': np.random.uniform(300000, 500000, num_anomalies)
    })
    
    return pd.concat([df, nonpractical], ignore_index=True)

# 3. افزودن منطق آسیب‌های آب‌نرمال ------------------------------------------------------
def add_damage_logic(df):
    # قوانین تجربی برای آسیب‌ها
    df['damage_type'] = 'Normal'
    
    # 1. Clay Swelling
 clay_cond = (df['clay'] > 25) & (df['pressure'] > 12000)
 df.loc[clay_cond, 'damage_type'] = 'ClaySwelling'
    
    # 2. Fluid Loss
 fluid_cond = (df['perm'] < 0.01) & (df['salinity'] > 200000)
 df.loc[fluid_cond, 'damage_type'] = 'FluidLoss'
    
    # 3. Scale Formation
 scale_cond = (df['temp'] > 150) & (df['salinity'] > 180000)
 df.loc[scale_cond, 'damage_type'] = 'ScaleFormation'
    
    # 4. Non-Practical Anomalies
 nonpractical_cond = (df['perm'] < 0) | (df['pressure'] > 20000)
 df.loc[nonpractical_cond, 'damage_type'] = 'NonPractical_Anomaly'
    
    return df

# 4. پاک‌سازی هوشمند داده‌ها ------------------------------------------------------------
def intelligent_cleaning(df):
    # حذف داده‌های غیرفیزیکی بی‌معنی
 df = df[
        (df['perm'] > 0.0001) &  # نفوذپذیری مثبت بسیار کم
        (df['temp'] < 350) &     # دمای غیرممکن
        (df['clay'] < 60)        # رس غیرواقعی
    ]
    
    # تشخیص Outlierهای آماری
 clf = IsolationForest(contamination=0.01, random_state=42)
 outliers = clf.fit_predict(df[['pressure', 'temp', 'perm']])
 df = df[outliers == 1]
    
    # حفظ Outlierهای معنادار
 domain_outliers = df[
        (df['damage_type'] != 'Normal') | 
        (df['perm'] < 0) | 
        (df['pressure'] > 18000)
    ]
    
    return domain_outliers

# 5. افزودن متا داده‌های عملیاتی --------------------------------------------------------
def add_metadata(df):
    # شناسه چاه
 df['well_id'] = ['Well_' + str(i).zfill(10) for i in range(len(df))]
    
    # زمان اندازه‌گیری
 start_date = datetime(2020, 1, 1)
 df['timestamp'] = [start_date + timedelta(minutes=10*i) for i in range(len(df))]
    
    # نوع سیال
 df['fluid_type'] = np.random.choice(
        ['Water', 'Oil', 'Gas', 'MultiPhase'],
 size=len(df),
 p=[0.4, 0.3, 0.2, 0.1]
    )
    
    # جهت تنش
 df['stress_orientation'] = np.random.randint(0, 360, len(df))
    
    return df

# اجرای کامل خط لوله -------------------------------------------------------------------
if __name__ == "__main__":
    # تولید داده اولیه
 core_df = generate_core_data()
    
    # افزودن داده‌های نان پرکتیکال
 with_nonpractical = add_nonpractical_data(core_df)
    
    # افزودن منطق آسیب‌ها
 with_damage = add_damage_logic(with_nonpractical)
    
    # پاک‌سازی هوشمند
 cleaned_data = intelligent_cleaning(with_damage)
    
    # افزودن متاداده
 final_df = add_metadata(cleaned_data)
    
    # ذخیره‌سازی
 final_df.to_parquet(
        'formation_damage_final_dataset.parquet',
        index=False,
        engine='pyarrow',
        compression='brotli'
    )
    
    # اعتبارسنجی
 print(f"تعداد رکوردهای نهایی: {len(final_df):,}")
 print("توزیع آسیب‌ها:")
 print(final_df['damage_type'].value_counts())