import pandas as pd
import numpy as np

# Number of records
num_samples = 1_000_000

# Categories and ranges
damage_types = [
    "Clay & Iron", "Drilling Damage", "Fluid Loss", "Fluid Incompatibility", "Emulsion", 
    "Rock/Fluid Interaction", "Completion Issue", "Corrosion Cracking", 
    "Filtration Problem", "Ultra-Clean Fluid"
]
formations = ["Carbonate", "Sandstone", "Shale", "Dolomite", "Mixed"]
fluid_types = ["Brine", "Acid", "Mud", "Water-Based", "Oil-Based"]
completion_types = ["Open Hole", "Cased Hole", "Perforated", "Liner"]

# Numerical ranges
temperature_range = (50, 200)  # Celsius
pressure_range = (1000, 15000)  # psi
ph_range = (3.5, 9.0)
salinity_range = (10_000, 250_000)  # ppm
flow_rate_range = (10, 1500)  # bbl/day
permeability_range = (0.01, 500)  # mD
porosity_range = (5, 35)  # %

# Generate synthetic data
np.random.seed(42)
data = {
    "Well_ID": [f"WELL_{i:06}" for i in range(num_samples)],
    "Formation": np.random.choice(formations, num_samples),
    "Fluid_Type": np.random.choice(fluid_types, num_samples),
    "Completion_Type": np.random.choice(completion_types, num_samples),
    "Temperature_C": np.random.uniform(*temperature_range, num_samples),
    "Pressure_psi": np.random.uniform(*pressure_range, num_samples),
    "pH": np.random.uniform(*ph_range, num_samples),
    "Salinity_ppm": np.random.uniform(*salinity_range, num_samples),
    "Flow_Rate_bbl_day": np.random.uniform(*flow_rate_range, num_samples),
    "Permeability_mD": np.random.uniform(*permeability_range, num_samples),
    "Porosity_pct": np.random.uniform(*porosity_range, num_samples),
    "Damage_Type": np.random.choice(damage_types, num_samples)
}

# Create and save DataFrame
df = pd.DataFrame(data)
df.to_csv("formation_damage_dataset.csv", index=False)

print("✅ Dataset generated and saved as 'formation_damage_dataset.csv'")
