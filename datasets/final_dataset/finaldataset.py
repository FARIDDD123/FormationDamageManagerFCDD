import numpy as np 
import pandas as pd  
import random  
from datetime import datetime, timedelta 

NUM_WELLS = 10  # تعداد چاه‌ها
RECORDS_PER_WELL = 1_000_000  # تعداد رکوردهای هر چاه

# لیستی از دیکشنری‌ها حاوی اطلاعات چاه‌های واقعی در سازند هینزویل (شامل شناسه چاه، طول جغرافیایی و عرض جغرافیایی)
wells_info = [
    {'well_id': '50', 'LONG': -94.86, 'LAT': 32.26},
    {'well_id': '31881', 'LONG': -94.82, 'LAT': 32.26},
    {'well_id': '34068', 'LONG': -94.78, 'LAT': 32.25},
    {'well_id': '81715', 'LONG': -94.95, 'LAT': 32.17},
    {'well_id': '35068', 'LONG': -94.18, 'LAT': 32.32},
    {'well_id': '362', 'LONG': -94.13, 'LAT': 32.32},
    {'well_id': '30944', 'LONG': -94.15, 'LAT': 32.12},
    {'well_id': '32094', 'LONG': -94.62, 'LAT': 32.37},
    {'well_id': '31921', 'LONG': -94.60, 'LAT': 32.37},
    {'well_id': '87931', 'LONG': -94.86, 'LAT': 32.45},
]

# محدوده‌های مجاز برای هر یک از پارامترهای چاه
ranges = {
    'depth': (3000, 4000),  # عمق (فوت)
    'porosity': (4.0, 8.0),  # تخلخل (درصد)
    'permeability': (50, 224),  # نفوذپذیری (میلی دارسی)
    'pressure': (4000, 5800),  # فشار (psi)
    'temperature': (132, 160),  # دما (فارنهایت)
    'clay_content': (5, 40),  # محتوای رس (درصد)
    'illite_content': (2, 15),  # محتوای ایلیت (درصد)
    'kaolinite_content': (1, 10),  # محتوای کائولینیت (درصد)
    'iron_content': (1, 15),  # محتوای آهن (درصد)
    'quartz_content': (20, 40),  # محتوای کوارتز (درصد)
    'calcite_content': (10, 30),  # محتوای کلسیت (درصد)
    'mud_weight': (8, 12),  # وزن گل حفاری (پوند بر گالن)
    'mud_viscosity': (10, 40),  # ویسکوزیته گل (سانتی پویز)
    'yp': (0, 20),  # تنش تسلیم (پوند بر 100 فوت مربع)
    'gel_strength': (0, 15),  # استحکام ژل (پوند بر 100 فوت مربع)
    'ph': (7, 12),  # میزان اسیدیته
    'salinity': (10000, 80000),  # شوری (ppm)
    'lime_content': (0, 5),  # محتوای آهک (درصد)
    'rop': (50, 250),  # نرخ نفوذ (فوت بر ساعت)
    'wob': (5000, 25000),  # وزن روی مته (پوند)
    'rpm': (50, 150),  # دور در دقیقه
    'flow_rate': (500, 1200),  # نرخ جریان (گالن بر دقیقه)
    'ecd': (10, 14),  # چگالی معادل گردشی (پوند بر گالن)
    'overbalance': (200, 800),  # اضافه فشار (psi)
    'perforation_density': (4, 12),  # تراکم سوراخ‌ها (سوراخ بر فوت)
    'brittleness_index': (0.4, 0.95),  # شاخص شکنندگی
    'clay_reactivity': (0.0, 16.5),  # واکنش‌پذیری رس
    'stress_ratio': (3.0, 3.4),  # نسبت تنش
    'fluid_incompatibility': (0.2, 0.8),  # ناسازگاری سیال
}

# انواع سیالات مورد استفاده
fluid_types = ['Water-Based', 'Oil-Based', 'Synthetic']
# انواع روش‌های تکمیل چاه
completion_types = ['Cased Hole', 'Open Hole', 'Slotted Liner']
# روش‌های تحریک چاه
stimulation_methods = ['Acidizing', 'Fracturing', 'None']

# انواع آسیب‌های احتمالی
damage_types = [
    'No_Damage',  # بدون آسیب
    'Clay_Iron_Control',  # کنترل رس و آهن
    'Drilling_Damage',  # آسیب حفاری
    'Fluid_Loss',  # از دست دادن سیال
    'Incompatibility',  # ناسازگاری
    'Near_Wellbore_Emulsions',  # امولسیون‌های نزدیک به چاه
    'Rock_Fluid_Interactions',  # برهمکنش سنگ و سیال
    'Completion_Connectivity',  # اتصال در تکمیل چاه
    'Cracking_Corrosion_Stress',  # ترک‌خوردگی، خوردگی و تنش
    'Surface_Filtration',  # فیلتراسیون سطحی
    'Ultra_Clean_Fluids',  # سیالات فوق تمیز
]

# وزن احتمال هر نوع آسیب
damage_weights = {
    'No_Damage': 0.30,  # 30% احتمال بدون آسیب
    'Clay_Iron_Control': 0.05,
    'Drilling_Damage': 0.05,
    'Fluid_Loss': 0.15,
    'Incompatibility': 0.05,
    'Near_Wellbore_Emulsions': 0.05,
    'Rock_Fluid_Interactions': 0.20,
    'Completion_Connectivity': 0.05,
    'Cracking_Corrosion_Stress': 0.05,
    'Surface_Filtration': 0.03,
    'Ultra_Clean_Fluids': 0.02,
}

def assign_damage(row):
    """
    نسخه کامل و پیشرفته تخصیص آسیب با فعال‌سازی تمامی پارامترها، براساس شرایط عملیاتی، زمین‌شناسی و یافته‌های SPE در سازند Haynesville.
    """
    p = random.random()

    # شرایط اصلی و ترکیبی
    high_pressure = row['pressure'] > 5200
    high_temp = row['temperature'] > 145
    clay_sensitive = row['clay_content'] > 20
    illite_rich = row['illite_content'] > 10
    incompatible_fluid = (row['fluid_type'] == 'Water-Based') and clay_sensitive
    low_stress_ratio = row['stress_ratio'] < 3.2
    high_rop = row['rop'] > 200
    low_gel = row['gel_strength'] < 5
    high_overbalance = row['overbalance'] > 600
    high_ecd = row['ecd'] > 13
    emulsions_risk = (row['fluid_type'] == 'Oil-Based') and (row['completion_type'] == 'Cased Hole')
    scaling_risk = row['calcite_content'] > 25 and row['salinity'] > 70000
    multi_factor_emulsion = (row['rop'] > 220 and row['mud_weight'] < 9 and row['fluid_type'] == 'Oil-Based')
    surf_filtration_risk = high_ecd and high_overbalance
    high_rpm = row['rpm'] > 130
    rpm_emulsion_risk = high_rpm and row['fluid_type'] == 'Oil-Based'
    rpm_drill_damage = high_rpm and row['wob'] > 20000
    rpm_filtration_risk = high_rpm and row['mud_weight'] < 9.5
    low_yp = row['yp'] < 5
    low_viscosity = row['mud_viscosity'] < 15
    brittle_rock = row['brittleness_index'] > 0.85
    low_perf_density = row['perforation_density'] < 6
    high_quartz = row['quartz_content'] > 35
    low_lime = row['lime_content'] < 1.0
    high_flow_rate = row['flow_rate'] > 1000

    cumulative = 0
    for damage, weight in damage_weights.items():
        w = weight

        # وزن‌دهی هوشمند و پویای کامل
        if damage == 'Fluid_Loss' and low_stress_ratio:
            w *= 3
        if damage == 'Clay_Iron_Control' and (clay_sensitive or illite_rich):
            w *= 2.5
        if damage == 'Rock_Fluid_Interactions' and (high_pressure or high_temp):
            w *= 2
        if damage == 'Incompatibility' and incompatible_fluid:
            w *= 3
        if damage == 'Drilling_Damage' and (high_rop and low_gel):
            w *= 2
        if damage == 'Drilling_Damage' and rpm_drill_damage:
            w *= 1.8
        if damage == 'Drilling_Damage' and (low_yp or low_viscosity):
            w *= 1.6
        if damage == 'Surface_Filtration' and surf_filtration_risk:
            w *= 2.5
        if damage == 'Surface_Filtration' and scaling_risk:
            w *= 1.5
        if damage == 'Surface_Filtration' and rpm_filtration_risk:
            w *= 1.4
        if damage == 'Surface_Filtration' and low_viscosity:
            w *= 1.3
        if damage == 'Near_Wellbore_Emulsions' and emulsions_risk:
            w *= 2
        if damage == 'Near_Wellbore_Emulsions' and multi_factor_emulsion:
            w *= 2.2
        if damage == 'Near_Wellbore_Emulsions' and rpm_emulsion_risk:
            w *= 1.5
        if damage == 'Near_Wellbore_Emulsions' and high_flow_rate:
            w *= 1.4
        if damage == 'Cracking_Corrosion_Stress' and (high_temp and row['ph'] > 10):
            w *= 2
        if damage == 'Cracking_Corrosion_Stress' and brittle_rock:
            w *= 1.5
        if damage == 'Ultra_Clean_Fluids' and (row['mud_weight'] < 9 and row['salinity'] < 15000):
            w *= 1.8
        if damage == 'Clay_Iron_Control' and row['salinity'] < 20000:
            w *= 1.3
        if damage == 'Incompatibility' and row['salinity'] > 60000:
            w *= 1.5
        if damage == 'Completion_Connectivity' and row['completion_type'] == 'Open Hole':
            w *= 2
        if damage == 'Completion_Connectivity' and low_perf_density:
            w *= 1.6
        if damage == 'Rock_Fluid_Interactions' and row['stimulation_method'] == 'Acidizing':
            w *= 1.8
        if damage == 'Completion_Connectivity' and row['stimulation_method'] == 'Fracturing':
            w *= 1.5
        if damage == 'Rock_Fluid_Interactions' and high_quartz and brittle_rock:
            w *= 1.6
        if damage == 'No_Damage' and (high_pressure and high_temp and not incompatible_fluid):
            w *= 0.4
        if damage == 'Ultra_Clean_Fluids' and low_lime:
            w *= 1.5

        cumulative += w
        if p < cumulative:
            return damage

    return 'No_Damage'

def generate_well_data(well):
    print(f"در حال تولید داده برای چاه {well['well_id']} ...")

    np.random.seed(hash(well['well_id']) % (2**32 - 1))
    random.seed(hash(well['well_id']) % (2**32 - 1))

    base_time = datetime(2023, 1, 1)

    df = pd.DataFrame({
        'record_id': [f"{well['well_id']}-{i+1:07d}" for i in range(RECORDS_PER_WELL)],
        'well_id': well['well_id'],
        'LONG': np.full(RECORDS_PER_WELL, well['LONG'], dtype=np.float32),
        'LAT': np.full(RECORDS_PER_WELL, well['LAT'], dtype=np.float32),
        'timestamp': [base_time + timedelta(minutes=i) for i in range(RECORDS_PER_WELL)],
    })

    # عمق و نرمال‌سازی آن
    df['depth'] = np.linspace(3000, 4000, RECORDS_PER_WELL).astype(np.float32)
    depth_norm = (df['depth'] - 3000) / 1000

    # فشار و دما - روابط غیرخطی
    df['pressure'] = (4000 + 2000 * depth_norm ** 1.1 + np.random.normal(0, 80, RECORDS_PER_WELL)).astype(np.float32)
    df['temperature'] = (132 + 28 * depth_norm ** 1.2 + np.random.normal(0, 2, RECORDS_PER_WELL)).astype(np.float32)

    # تخلخل و نفوذپذیری
    df['porosity'] = np.clip(8 - 4 * depth_norm + np.random.normal(0, 0.2, RECORDS_PER_WELL), 4.0, 8.0).astype(np.float32)
    df['permeability'] = np.clip((df['porosity'] ** 3) * 0.7 + np.random.normal(0, 5, RECORDS_PER_WELL), 50, 224).astype(np.float32)

    # ترکیب کانی‌ها
    df['illite_content'] = np.random.uniform(2, 15, RECORDS_PER_WELL).astype(np.float32)
    df['clay_content'] = np.clip(df['illite_content'] * 1.5 + np.random.normal(0, 2, RECORDS_PER_WELL), 5, 40).astype(np.float32)
    df['quartz_content'] = np.clip(40 - df['clay_content'] * 0.5 + np.random.normal(0, 1, RECORDS_PER_WELL), 20, 40).astype(np.float32)
    df['calcite_content'] = np.random.uniform(10, 30, RECORDS_PER_WELL).astype(np.float32)
    df['iron_content'] = np.random.uniform(1, 15, RECORDS_PER_WELL).astype(np.float32)
    df['kaolinite_content'] = np.random.uniform(1, 10, RECORDS_PER_WELL).astype(np.float32)

    # شاخص شکنندگی
    effective_stress = df['pressure'] - df['depth'] * 0.465
    df['brittleness_index'] = np.clip(0.4 + 0.005 * df['quartz_content'] + 0.00002 * effective_stress - 0.001 * df['permeability'], 0.4, 0.95)

    # نوع سیال، تکمیل، تحریک
    df['fluid_type'] = np.random.choice(fluid_types, RECORDS_PER_WELL)
    df['completion_type'] = np.random.choice(completion_types, RECORDS_PER_WELL)
    df['stimulation_method'] = np.random.choice(stimulation_methods, RECORDS_PER_WELL)

    # ویژگی‌های سیال بر اساس نوع
    fluid_base = {'Water-Based': (8.6, 18), 'Oil-Based': (10.5, 30), 'Synthetic': (9.3, 22)}
    df['mud_weight'] = df['fluid_type'].map(lambda x: np.random.normal(fluid_base[x][0], 0.3)).astype(np.float32)
    df['mud_viscosity'] = df['fluid_type'].map(lambda x: np.random.normal(fluid_base[x][1], 5)).astype(np.float32)

    # خواص حفاری و سیال
    df['yp'] = np.clip(np.random.normal(10, 5, RECORDS_PER_WELL), 0, 20).astype(np.float32)
    df['gel_strength'] = np.clip(np.random.normal(7, 4, RECORDS_PER_WELL), 0, 15).astype(np.float32)
    df['ph'] = np.random.uniform(7, 12, RECORDS_PER_WELL).astype(np.float32)
    df['salinity'] = np.random.uniform(10000, 80000, RECORDS_PER_WELL).astype(np.float32)
    df['lime_content'] = np.random.uniform(0, 5, RECORDS_PER_WELL).astype(np.float32)

    # نرخ نفوذ ROP
    df['rop'] = np.clip(250 - 100 * depth_norm + 0.1 * df['pressure'] + 20 * df['brittleness_index'] + np.random.normal(0, 10, RECORDS_PER_WELL), 50, 250).astype(np.float32)

    # سایر پارامترهای عملیاتی
    df['wob'] = np.random.uniform(5000, 25000, RECORDS_PER_WELL).astype(np.float32)
    df['rpm'] = np.random.uniform(50, 150, RECORDS_PER_WELL).astype(np.float32)
    df['flow_rate'] = np.random.uniform(500, 1200, RECORDS_PER_WELL).astype(np.float32)
    df['ecd'] = np.random.uniform(10, 14, RECORDS_PER_WELL).astype(np.float32)
    df['overbalance'] = np.random.uniform(200, 800, RECORDS_PER_WELL).astype(np.float32)
    df['perforation_density'] = np.random.uniform(4, 12, RECORDS_PER_WELL).astype(np.float32)
    df['clay_reactivity'] = np.random.uniform(0.0, 16.5, RECORDS_PER_WELL).astype(np.float32)
    df['stress_ratio'] = np.random.uniform(3.0, 3.4, RECORDS_PER_WELL).astype(np.float32)
    df['fluid_incompatibility'] = np.random.uniform(0.2, 0.8, RECORDS_PER_WELL).astype(np.float32)

    # نویز هدفمند
    noise_mask = np.random.rand(RECORDS_PER_WELL) < 0.02
    df.loc[noise_mask, 'mud_weight'] += np.random.normal(2.5, 0.5, noise_mask.sum())
    df.loc[noise_mask, 'quartz_content'] = 15 + np.random.rand(noise_mask.sum()) * 5

    # تخصیص نوع آسیب
    df['damage_type'] = df.apply(assign_damage, axis=1)

    return df


def optimize_and_save(df, filename):
    """
    تابعی برای بهینه‌سازی نوع داده‌ها و ذخیره‌سازی فشرده به فرمت Parquet
    
    پارامترها:
        df (pd.DataFrame): دیتافریم تولید شده برای یک چاه
        filename (str): مسیر و نام فایل خروجی Parquet
        
    برمی‌گرداند:
        None: فایل بهینه‌شده در دیسک ذخیره می‌شود
    """
    float_cols = df.select_dtypes(include='float64').columns
    df[float_cols] = df[float_cols].astype(np.float32)

    int_cols = df.select_dtypes(include='int64').columns
    df[int_cols] = df[int_cols].astype(np.int32)

    cat_cols = ['fluid_type', 'completion_type', 'stimulation_method', 'damage_type']
    for col in cat_cols:
        df[col] = df[col].astype('category')

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    df.to_parquet(filename, index=False, compression='snappy')

# حلقه اصلی برای تولید داده برای هر چاه و ذخیره در فایل
for well in wells_info:
    df_well = generate_well_data(well)
    filename = f"Haynesville_{well['well_id']}.parquet"
    optimize_and_save(df_well, filename)
    print(f"فایل {filename} ذخیره شد")

print("تولید داده با موفقیت انجام شد.")