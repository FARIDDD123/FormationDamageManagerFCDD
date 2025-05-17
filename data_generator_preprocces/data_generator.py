import pandas as pd
import numpy as np
from sklearn.utils import shuffle

# ======================= Basic Settings =======================
all_data = 10_000
NUM_NORMAL = int(all_data * 0.95)
NUM_ABNORMAL = int(all_data*0.05)  # 5% outliers
OUTPUT_FILE = "./datasets/formation_damage_optimized.parquet"

# ======================= Variable Definitions =======================
damage_types = [
    "Clay & Iron", "Drilling Damage", "Fluid Loss", "Fluid Incompatibility", 
    "Emulsion", "Rock/Fluid Interaction", "Completion Issue", 
    "Corrosion Cracking", "Filtration Problem", "Ultra-Clean Fluid"
]
formations = ["Carbonate", "Sandstone", "Shale", "Dolomite", "Mixed"]
fluid_types = ["Brine", "Acid", "Mud", "Water-Based", "Oil-Based"]
completion_types = ["Open Hole", "Cased Hole", "Perforated", "Liner"]

# Normal value ranges
normal_ranges = {
    "Temperature_C": (50, 200),
    "Pressure_psi": (1000, 15000),
    "pH": (3.5, 9.0),
    "Salinity_ppm": (10_000, 250_000),
    "Flow_Rate_bbl_day": (10, 1500),
    "Permeability_mD": (0.01, 500),
    "Porosity_pct": (5, 35)
}

# Outlier value ranges (for Task #1)
abnormal_ranges = {
    "Temperature_C": (220, 400),
    "Pressure_psi": (16000, 30000),
    "pH": (0.5, 3.4),
    "Salinity_ppm": (300_000, 1_000_000),
    "Flow_Rate_bbl_day": (1600, 10_000),
    "Permeability_mD": (600, 5000),
    "Porosity_pct": (0, 4)
}

# ======================= Generating Normal Data =======================
np.random.seed(42)
normal_data = {
    "Well_ID": [f"WELL_{i:07}" for i in range(NUM_NORMAL)],
    "Formation": np.random.choice(formations, NUM_NORMAL),
    "Fluid_Type": np.random.choice(fluid_types, NUM_NORMAL),
    "Completion_Type": np.random.choice(completion_types, NUM_NORMAL),
    "Temperature_C": np.random.uniform(*normal_ranges["Temperature_C"], NUM_NORMAL).astype(np.float32),
    "Pressure_psi": np.random.uniform(*normal_ranges["Pressure_psi"], NUM_NORMAL).astype(np.float32),
    "pH": np.random.uniform(*normal_ranges["pH"], NUM_NORMAL).astype(np.float32),
    "Salinity_ppm": np.random.uniform(*normal_ranges["Salinity_ppm"], NUM_NORMAL).astype(np.float32),
    "Flow_Rate_bbl_day": np.random.uniform(*normal_ranges["Flow_Rate_bbl_day"], NUM_NORMAL).astype(np.float32),
    "Permeability_mD": np.random.uniform(*normal_ranges["Permeability_mD"], NUM_NORMAL).astype(np.float32),
    "Porosity_pct": np.random.uniform(*normal_ranges["Porosity_pct"], NUM_NORMAL).astype(np.float32),
    "Damage_Type": np.random.choice(damage_types, NUM_NORMAL)
}

# ======================= Generating Outlier Data =======================
np.random.seed(123)
abnormal_data = {
    "Well_ID": [f"ABN_{i:07}" for i in range(NUM_ABNORMAL)],
    "Formation": np.random.choice(formations, NUM_ABNORMAL),
    "Fluid_Type": np.random.choice(fluid_types, NUM_ABNORMAL),
    "Completion_Type": np.random.choice(completion_types, NUM_ABNORMAL),
    "Temperature_C": np.random.uniform(*abnormal_ranges["Temperature_C"], NUM_ABNORMAL).astype(np.float32),
    "Pressure_psi": np.random.uniform(*abnormal_ranges["Pressure_psi"], NUM_ABNORMAL).astype(np.float32),
    "pH": np.random.uniform(*abnormal_ranges["pH"], NUM_ABNORMAL).astype(np.float32),
    "Salinity_ppm": np.random.uniform(*abnormal_ranges["Salinity_ppm"], NUM_ABNORMAL).astype(np.float32),
    "Flow_Rate_bbl_day": np.random.uniform(*abnormal_ranges["Flow_Rate_bbl_day"], NUM_ABNORMAL).astype(np.float32),
    "Permeability_mD": np.random.uniform(*abnormal_ranges["Permeability_mD"], NUM_ABNORMAL).astype(np.float32),
    "Porosity_pct": np.random.uniform(*abnormal_ranges["Porosity_pct"], NUM_ABNORMAL).astype(np.float32),
    "Damage_Type": np.random.choice(["Corrosion Cracking", "Fluid Incompatibility"], NUM_ABNORMAL)  # Focus on critical damage types
}

# ======================= Merging and Saving =======================
df_normal = pd.DataFrame(normal_data)
df_abnormal = pd.DataFrame(abnormal_data)
df_combined = pd.concat([df_normal, df_abnormal], ignore_index=True)

# Adding artificial missing values (for Task #3)
df_combined.loc[df_combined.sample(frac=0.05, random_state=42).index, "Salinity_ppm"] = np.nan  # 5% missing data

# Shuffle the dataset
df_final = shuffle(df_combined, random_state=42).reset_index(drop=True)

# Optimizing data types
df_final = df_final.astype({
    "Well_ID": "category",
    "Formation": "category",
    "Fluid_Type": "category",
    "Completion_Type": "category",
    "Damage_Type": "category"
})

# Saving the dataset
df_final.to_parquet(OUTPUT_FILE, index=False)
print(f"✅ Final dataset with {NUM_NORMAL + NUM_ABNORMAL:,} records saved to '{OUTPUT_FILE}'.")