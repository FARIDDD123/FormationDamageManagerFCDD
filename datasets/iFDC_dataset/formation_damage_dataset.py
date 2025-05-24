import pandas as pd
import numpy as np
from faker import Faker
import random
from sklearn.preprocessing import MinMaxScaler

# تنظیمات اولیه
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)
n = 1_000_000

formation_types = ['Sandstone', 'Limestone', 'Dolomite', 'Shale', 'Siltstone', 'Chalk']

# تولید داده‌ها
df = pd.DataFrame({
    'well_id': [f'HZ-{i:07d}' for i in range(1, n+1)],
    'spud_date': [fake.date_between('-5y', '-1y') for _ in range(n)],
    'completion_date': [fake.date_between('-1y', 'today') for _ in range(n)],
    'depth': np.random.uniform(3000, 4000, n),
    'porosity': np.random.normal(6, 1, n).clip(4, 8),
    'permeability': np.random.lognormal(5, 0.5, n).clip(50, 500),
    'pressure': np.random.uniform(5000, 7000, n),
    'temperature': np.random.uniform(150, 175, n),
    'clay_content': np.random.uniform(5, 40, n),
    'illite_content': np.random.uniform(0, 15, n),
    'kaolinite_content': np.random.uniform(0, 20, n),
    'iron_content': np.random.uniform(0.1, 5, n),
    'quartz_content': np.random.uniform(30, 70, n),
    'calcite_content': np.random.uniform(0, 25, n),
    'fluid_type': random.choices(['Water-Based', 'Oil-Based', 'Synthetic'], [0.6, 0.3, 0.1], k=n),
    'mud_weight': np.random.uniform(10, 15, n),
    'mud_viscosity': np.random.uniform(30, 60, n),
    'yp': np.random.uniform(10, 30, n),
    'gel_strength': np.random.uniform(5, 20, n),
    'ph': np.random.uniform(6, 9, n),
    'salinity': np.random.uniform(5000, 50000, n),
    'lime_content': np.random.uniform(0, 5, n),
    'rop': np.random.uniform(10, 30, n),
    'wob': np.random.uniform(5000, 25000, n),
    'rpm': np.random.uniform(50, 150, n),
    'flow_rate': np.random.uniform(500, 1200, n),
    'ecd': np.random.uniform(10, 14, n),
    'overbalance': np.random.uniform(200, 800, n),
    'completion_type': random.choices(['Open Hole', 'Cased Hole', 'Slotted Liner'], [0.3, 0.5, 0.2], k=n),
    'perforation_density': np.random.uniform(4, 12, n),
    'stimulation_method': random.choices(['Acidizing', 'Fracturing', 'None'], [0.4, 0.4, 0.2], k=n),
})

# ستون formation
df['formation'] = random.choices(
    population=formation_types,
    weights=[0.3, 0.25, 0.15, 0.2, 0.05, 0.05],
    k=n
)

# ویژگی‌های مشتق‌شده
df['brittleness_index'] = (df['quartz_content'] + df['calcite_content']) / (
    df['quartz_content'] + df['calcite_content'] + df['clay_content'])
df['clay_reactivity'] = (df['illite_content'] * 0.7 + df['kaolinite_content'] * 0.3) * df['ph'] / 9
df['stress_ratio'] = df['pressure'] / (df['depth'] * 0.433)

df['fluid_incompatibility'] = np.select(
    [
        (df['fluid_type'] == 'Water-Based') & (df['salinity'] > 30000),
        (df['fluid_type'] == 'Oil-Based') & (df['temperature'] > 170)
    ],
    [0.8, 0.5],
    default=0.2
)

#  آیا آسیب رخ داده؟
damage_probability = np.random.uniform(0, 1, n)
df['damage_occurred'] = np.where(damage_probability > 0.3, 'Yes', 'No')

# تابع تعیین نوع آسیب
def get_damage_type(row):
    if row['damage_occurred'] == 'No':
        return 'No_Damage'
    scores = {
        'Clay_Iron_Control': 0.4 * row['clay_content']/40 + 0.3 * row['iron_content']/5 + 0.2 * row['ph']/9 + 0.1 * row['lime_content']/5,
        'Drilling_Damage': 0.5 * row['overbalance']/800 + 0.3 * row['rop']/30 + 0.2 * row['wob']/25000,
        'Fluid_Loss': 0.6 * row['permeability']/500 + 0.2 * row['mud_viscosity']/60 + 0.2 * row['ecd']/14,
        'Fluid_Incompatibility': 0.7 * row['fluid_incompatibility'] + 0.3 * row['salinity']/50000,
        'Near_Wellbore_Emulsions': 0.5 * (row['mud_weight'] - 10)/5 + 0.3 * row['flow_rate']/1200 + 0.2 * row['gel_strength']/20,
        'Rock_Fluid_Interactions': 0.6 * row['clay_reactivity'] + 0.4 * row['temperature']/175,
        'Completion_Connectivity': 0.5 * (1 if row['completion_type'] == 'Open Hole' else 0.5) + 0.3 * row['perforation_density']/12 + 0.2 * (1 if row['stimulation_method'] == 'None' else 0),
        'Cracking_Corrosion_Stress': 0.4 * row['stress_ratio'] + 0.3 * row['brittleness_index'] + 0.2 * row['iron_content']/5 + 0.1 * row['temperature']/175,
        'Surface_Filtration': 0.7 * row['mud_viscosity']/60 + 0.3 * row['yp']/30,
        'Ultra_Clean_Fluids': 0.8 * (1 if row['fluid_type'] == 'Synthetic' else 0.2) + 0.2 * row['salinity']/50000
    }
    norm_vals = MinMaxScaler().fit_transform(np.array(list(scores.values())).reshape(-1, 1)).flatten()
    norm_scores = dict(zip(scores.keys(), norm_vals))
    candidates = [k for k, v in norm_scores.items() if v > 0.65]
    return 'No_Damage' if not candidates else random.choice(candidates)

df['damage_type'] = df.apply(get_damage_type, axis=1)

# شدت آسیب
def get_severity(row):
    if row['damage_type'] == 'No_Damage':
        return 0.0
    base = {
        'Clay_Iron_Control': 0.4 * row['clay_content']/40 + 0.3 * row['iron_content']/5,
        'Drilling_Damage': 0.5 * row['overbalance']/800 + 0.3 * row['rop']/30,
        'Fluid_Loss': 0.6 * row['permeability']/500 + 0.2 * row['mud_viscosity']/60,
        'Fluid_Incompatibility': 0.7 * row['fluid_incompatibility'],
        'Near_Wellbore_Emulsions': 0.5 * (row['mud_weight'] - 10)/5 + 0.3 * row['flow_rate']/1200,
        'Rock_Fluid_Interactions': 0.6 * row['clay_reactivity'],
        'Completion_Connectivity': 0.5 * (1 if row['completion_type'] == 'Open Hole' else 0.5),
        'Cracking_Corrosion_Stress': 0.4 * row['stress_ratio'] + 0.3 * row['brittleness_index'],
        'Surface_Filtration': 0.7 * row['mud_viscosity']/60,
        'Ultra_Clean_Fluids': 0.8 * (1 if row['fluid_type'] == 'Synthetic' else 0.2),
    }
    return round(5 * base.get(row['damage_type'], 0), 1)

df['damage_severity'] = df.apply(get_severity, axis=1)

# تولید اولیه
def production(row):
    base = 15 - (row['depth'] - 3000) / 200
    if row['damage_type'] != 'No_Damage':
        loss_factor = {
            'Clay_Iron_Control': 0.8, 'Drilling_Damage': 0.9, 'Fluid_Loss': 0.7,
            'Fluid_Incompatibility': 0.6, 'Near_Wellbore_Emulsions': 0.5,
            'Rock_Fluid_Interactions': 0.7, 'Completion_Connectivity': 0.9,
            'Cracking_Corrosion_Stress': 1.0, 'Surface_Filtration': 0.4,
            'Ultra_Clean_Fluids': 0.3
        }.get(row['damage_type'], 0)
        base *= (1 - loss_factor * row['damage_severity'] / 25)
    return np.clip(base + np.random.normal(0, 1), 5, 20)

df['initial_production'] = df.apply(production, axis=1)
df['production_decline'] = np.where(df['damage_type'] == 'No_Damage',
                                    np.random.uniform(0.4, 0.6, n),
                                    np.random.uniform(0.5, 0.8, n))

# کاهش حجم داده
for col in df.select_dtypes('float64').columns:
    df[col] = df[col].astype(np.float32)
for col in df.select_dtypes('int64').columns:
    df[col] = df[col].astype(np.int32)

# افزودن داده گم‌شده
missing_cols = ['mud_weight', 'wob', 'rpm', 'flow_rate', 'yp']
for col in missing_cols:
    df.loc[df.sample(frac=0.05).index, col] = np.nan

# ذخیره نهایی
df.to_parquet("/formation_damage_dataset.parquet", index=False)
print("✅ فایل نهایی با ستون‌های formation و damage_occurred ذخیره شد.")