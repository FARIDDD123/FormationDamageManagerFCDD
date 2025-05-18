import pandas as pd
import numpy as np
from sklearn.utils import shuffle

# ======================= Basic Settings =======================
all_data = 10_000
NUM_NORMAL = int(all_data * 0.95)
NUM_ABNORMAL = all_data - NUM_NORMAL
OUTPUT_FILE = "./datasets/formation_damage_optimized.parquet"

# ======================= Categorical Variables =======================
damage_types = [
    "Clay & Iron", "Drilling Damage", "Fluid Loss", "Fluid Incompatibility", 
    "Emulsion", "Rock/Fluid Interaction", "Completion Issue", 
    "Corrosion Cracking", "Filtration Problem", "Ultra-Clean Fluid"
]
formations = ["Carbonate", "Sandstone", "Shale", "Dolomite", "Mixed"]
fluid_types = ["Brine", "Acid", "Mud", "Water-Based", "Oil-Based"]
completion_types = ["Open Hole", "Cased Hole", "Perforated", "Liner"]

np.random.seed(42)

# ======================= Helper Functions =======================

def generate_porosity(n):
    porosity = np.random.beta(2.5, 5, n) * 35  # skewed toward lower values
    return porosity.astype(np.float32)

def generate_permeability(porosity):
    noise = np.random.normal(0, 10, len(porosity))
    permeability = (porosity ** 1.5) + noise
    permeability = np.clip(permeability, 0.01, 500)
    return permeability.astype(np.float32)

def generate_temperature(n):
    temp = np.random.normal(120, 30, n)
    return np.clip(temp, 50, 200).astype(np.float32)

def generate_pressure(temp):
    pressure = temp * np.random.uniform(50, 80, len(temp)) + np.random.normal(0, 500, len(temp))
    return np.clip(pressure, 1000, 15000).astype(np.float32)

def generate_ph(n):
    return np.clip(np.random.normal(6.5, 1.5, n), 3.5, 9.0).astype(np.float32)

def generate_salinity(n):
    return np.clip(np.random.normal(120_000, 50_000, n), 10_000, 250_000).astype(np.float32)

def generate_flow_rate(n):
    return np.random.exponential(scale=300, size=n).clip(10, 1500).astype(np.float32)

def generate_damage_type(row):
    probs = {
        "Clay & Iron": 0.0,
        "Drilling Damage": 0.0,
        "Fluid Loss": 0.0,
        "Fluid Incompatibility": 0.0,
        "Emulsion": 0.0,
        "Rock/Fluid Interaction": 0.0,
        "Completion Issue": 0.0,
        "Corrosion Cracking": 0.0,
        "Filtration Problem": 0.0,
        "Ultra-Clean Fluid": 0.0,
        "No Damage": 0.0,
    }

    # شرایط مختلف و افزایش احتمال دمیج‌ها:
    if row["pH"] < 4 and row["Fluid_Type"] == "Acid":
        probs["Corrosion Cracking"] += 0.5
    if row["Formation"] == "Sandstone" and row["Salinity_ppm"] > 200_000:
        probs["Clay & Iron"] += 0.4
    if row["Flow_Rate_bbl_day"] < 50 and row["Permeability_mD"] < 10:
        probs["Drilling Damage"] += 0.5
    if row["pH"] > 8 and row["Fluid_Type"] == "Brine":
        probs["Emulsion"] += 0.4
    if row["Completion_Type"] == "Open Hole":
        probs["Fluid Loss"] += 0.3
    if row["Formation"] == "Dolomite" and row["Fluid_Type"] == "Oil-Based" and row["Temperature_C"] > 150:
        probs["Rock/Fluid Interaction"] += 0.3
    if row["Completion_Type"] == "Perforated" and row["Pressure_psi"] > 14000:
        probs["Completion Issue"] += 0.3
    if row["Salinity_ppm"] < 20_000 and row["Fluid_Type"] == "Water-Based":
        probs["Filtration Problem"] += 0.2
    if row["Flow_Rate_bbl_day"] > 1200 and row["pH"] > 7 and row["Formation"] == "Sandstone":
        probs["Ultra-Clean Fluid"] += 0.2
    if 5 <= row["pH"] <= 8 and 1000 <= row["Pressure_psi"] <= 10000:
        probs["No Damage"] += 0.7

    # اگر هیچ شرطی قوی نبود، احتمال no damage رو بالا ببر
    if sum(probs.values()) == 0:
        probs["No Damage"] = 1.0

    # نرمالیزه کردن احتمال‌ها به جمع ۱
    total = sum(probs.values())
    for key in probs:
        probs[key] /= total

    # انتخاب دمیج بر اساس توزیع احتمال
    damage = np.random.choice(list(probs.keys()), p=list(probs.values()))
    return damage

# ======================= Generate Normal Data =======================

porosity = generate_porosity(NUM_NORMAL)
temperature = generate_temperature(NUM_NORMAL)
pressure = generate_pressure(temperature)
ph = generate_ph(NUM_NORMAL)
salinity = generate_salinity(NUM_NORMAL)
flow_rate = generate_flow_rate(NUM_NORMAL)
permeability = generate_permeability(porosity)

normal_data = pd.DataFrame({
    "Well_ID": [f"WELL_{i:07}" for i in range(NUM_NORMAL)],
    "Formation": np.random.choice(formations, NUM_NORMAL),
    "Fluid_Type": np.random.choice(fluid_types, NUM_NORMAL),
    "Completion_Type": np.random.choice(completion_types, NUM_NORMAL),
    "Temperature_C": temperature + np.random.normal(0, 1, NUM_NORMAL),
    "Pressure_psi": pressure + np.random.normal(0, 50, NUM_NORMAL),
    "pH": ph,
    "Salinity_ppm": salinity,
    "Flow_Rate_bbl_day": flow_rate + np.random.normal(0, 10, NUM_NORMAL),
    "Porosity_pct": porosity,
    "Permeability_mD": permeability
})

# Apply rule-based damage assignment with "No Damage"
normal_data["Damage_Type"] = normal_data.apply(generate_damage_type, axis=1)

# ======================= Generate Abnormal Data =======================

np.random.seed(123)
abnormal_data = pd.DataFrame({
    "Well_ID": [f"ABN_{i:07}" for i in range(NUM_ABNORMAL)],
    "Formation": np.random.choice(formations, NUM_ABNORMAL),
    "Fluid_Type": np.random.choice(fluid_types, NUM_ABNORMAL),
    "Completion_Type": np.random.choice(completion_types, NUM_ABNORMAL),
    "Temperature_C": np.random.uniform(220, 400, NUM_ABNORMAL).astype(np.float32),
    "Pressure_psi": np.random.uniform(16000, 30000, NUM_ABNORMAL).astype(np.float32),
    "pH": np.random.uniform(0.5, 3.4, NUM_ABNORMAL).astype(np.float32),
    "Salinity_ppm": np.random.uniform(300_000, 1_000_000, NUM_ABNORMAL).astype(np.float32),
    "Flow_Rate_bbl_day": np.random.uniform(1600, 10_000, NUM_ABNORMAL).astype(np.float32),
    "Porosity_pct": np.random.uniform(0, 4, NUM_ABNORMAL).astype(np.float32),
    "Permeability_mD": np.random.uniform(600, 5000, NUM_ABNORMAL).astype(np.float32),
    # Abnormal data has only these damage types:
    "Damage_Type": np.random.choice(["Corrosion Cracking", "Fluid Incompatibility"], NUM_ABNORMAL)
})

# ======================= Combine & Clean =======================

df_all = pd.concat([normal_data, abnormal_data], ignore_index=True)

# Add artificial missing values
missing_indices = df_all.sample(frac=0.05, random_state=42).index
df_all.loc[missing_indices, "Salinity_ppm"] = np.nan

# Shuffle
df_all = shuffle(df_all, random_state=42).reset_index(drop=True)

# Optimize types
categorical_columns = ["Well_ID", "Formation", "Fluid_Type", "Completion_Type", "Damage_Type"]
for col in categorical_columns:
    df_all[col] = df_all[col].astype("category")

# ======================= Save =======================

try:
    df_all.to_parquet(OUTPUT_FILE, index=False)
    print(f"✅ Dataset saved to: {OUTPUT_FILE}")
except Exception as e:
    print("⚠️ خطا در ذخیره‌سازی فایل Parquet:", e)
    print("➡️ راه‌حل: نصب pyarrow با دستور: pip install pyarrow")
