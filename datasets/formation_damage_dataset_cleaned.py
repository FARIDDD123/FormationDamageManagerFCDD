import pandas as pd
import numpy as np
import os

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

# Create DataFrame
df = pd.DataFrame(data)

# -----------------------------
# Cleaning part starts here
# -----------------------------

# Columns to clean
columns_to_clean = ["Damage_Type", "Formation", "Fluid_Type", "Completion_Type"]

# Cleaning function
def clean_text(text):
    if pd.isnull(text):
        return text
    text = text.strip()                  # Remove leading/trailing spaces
    text = ' '.join(text.split())         # Remove multiple spaces
    text = text.lower()                   # Convert to lowercase
    return text

# Apply cleaning
for col in columns_to_clean:
    df[col] = df[col].apply(clean_text)

# Create directory for unique value files
output_dir = "unique_values"
os.makedirs(output_dir, exist_ok=True)

# Save cleaned unique values
for col in columns_to_clean:
    unique_values = df[col].dropna().unique()
    unique_df = pd.DataFrame({col: unique_values})
    unique_file_path = os.path.join(output_dir, f"{col}_unique_cleaned.csv")
    unique_df.to_csv(unique_file_path, index=False)
    print(f"✅ Unique values for '{col}' saved to '{unique_file_path}'")

# Save cleaned main DataFrame
df.to_csv("formation_damage_dataset_cleaned.csv", index=False)
print("✅ Cleaned dataset saved as 'formation_damage_dataset_cleaned.csv'")
