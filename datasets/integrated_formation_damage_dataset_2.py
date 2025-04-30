import pandas as pd
import numpy as np

# Number of records
normal_samples = 10_000_000
abnormal_samples = 100_000

# Categories and ranges
damage_types = [
    "Clay & Iron", "Drilling Damage", "Fluid Loss", "Fluid Incompatibility", "Emulsion", 
    "Rock/Fluid Interaction", "Completion Issue", "Corrosion Cracking", 
    "Filtration Problem", "Ultra-Clean Fluid"
]
formations = ["Carbonate", "Sandstone", "Shale", "Dolomite", "Mixed"]
fluid_types = ["Brine", "Acid", "Mud", "Water-Based", "Oil-Based"]
completion_types = ["Open Hole", "Cased Hole", "Perforated", "Liner"]

# Normal numerical ranges
ranges = {
    "Temperature_C": (50, 200),
    "Pressure_psi": (1000, 15000),
    "pH": (3.5, 9.0),
    "Salinity_ppm": (10_000, 250_000),
    "Flow_Rate_bbl_day": (10, 1500),
    "Permeability_mD": (0.01, 500),
    "Porosity_pct": (5, 35)
}

# Generate normal data
np.random.seed(42)
normal_data = {
    "Well_ID": [f"WELL_{i:07}" for i in range(normal_samples)],
    "Formation": np.random.choice(formations, normal_samples),
    "Fluid_Type": np.random.choice(fluid_types, normal_samples),
    "Completion_Type": np.random.choice(completion_types, normal_samples),
    "Temperature_C": np.random.uniform(*ranges["Temperature_C"], normal_samples).astype(np.float32),
    "Pressure_psi": np.random.uniform(*ranges["Pressure_psi"], normal_samples).astype(np.float32),
    "pH": np.random.uniform(*ranges["pH"], normal_samples).astype(np.float32),
    "Salinity_ppm": np.random.uniform(*ranges["Salinity_ppm"], normal_samples).astype(np.float32),
    "Flow_Rate_bbl_day": np.random.uniform(*ranges["Flow_Rate_bbl_day"], normal_samples).astype(np.float32),
    "Permeability_mD": np.random.uniform(*ranges["Permeability_mD"], normal_samples).astype(np.float32),
    "Porosity_pct": np.random.uniform(*ranges["Porosity_pct"], normal_samples).astype(np.float32),
    "Damage_Type": np.random.choice(damage_types, normal_samples)
}

# Generate abnormal data with out-of-bound values
abnormal_data = {
    "Well_ID": [f"ABNORM_{i:07}" for i in range(abnormal_samples)],
    "Formation": np.random.choice(formations, abnormal_samples),
    "Fluid_Type": np.random.choice(fluid_types, abnormal_samples),
    "Completion_Type": np.random.choice(completion_types, abnormal_samples),
    "Temperature_C": np.random.uniform(220, 400, abnormal_samples).astype(np.float32),  # High temp
    "Pressure_psi": np.random.uniform(16000, 30000, abnormal_samples).astype(np.float32),  # High pressure
    "pH": np.random.uniform(0.5, 3.4, abnormal_samples).astype(np.float32),  # Low pH
    "Salinity_ppm": np.random.uniform(300_000, 1_000_000, abnormal_samples).astype(np.float32),  # High salinity
    "Flow_Rate_bbl_day": np.random.uniform(1600, 10000, abnormal_samples).astype(np.float32),  # High flow
    "Permeability_mD": np.random.uniform(600, 5000, abnormal_samples).astype(np.float32),  # Very high perm
    "Porosity_pct": np.random.uniform(0, 4, abnormal_samples).astype(np.float32),  # Very low porosity
    "Damage_Type": np.random.choice(damage_types, abnormal_samples)
}

# Create DataFrames
df_normal = pd.DataFrame(normal_data)
df_abnormal = pd.DataFrame(abnormal_data)

# Integrate and shuffle
df_combined = pd.concat([df_normal, df_abnormal], ignore_index=True)
df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

# Optimize dtypes
df_combined = df_combined.astype({
    "Well_ID": "category",
    "Formation": "category",
    "Fluid_Type": "category",
    "Completion_Type": "category",
    "Damage_Type": "category"
})

# Save to compressed CSV
df_combined.to_csv(
    "integrated_formation_damage_dataset.csv",
    index=False
)

print("✅ Integrated dataset with normal + abnormal records saved as 'integrated_formation_damage_dataset.csv'")
