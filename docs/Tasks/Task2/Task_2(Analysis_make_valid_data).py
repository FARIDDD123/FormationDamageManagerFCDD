import pandas as pd

# Load the data from local file
df = pd.read_parquet("formation_damage_cleaned.parquet")

# Define invalid combinations using vectorized conditions
cond1 = (df['Formation'] == 'Shale') & (df['Fluid_Type'] == 'Acidic') & (df['Completion_Type'] == 'Open Hole')
cond2 = (df['Formation'] == 'Carbonate') & (df['Fluid_Type'] == 'Brine') & (df['Completion_Type'] == 'Open Hole')
cond3 = (df['Formation'] == 'Sandstone') & (df['Fluid_Type'] == 'Water-Based') & (df['Completion_Type'] == 'Perforated')
cond4 = (df['Formation'] == 'Shale') & (df['Fluid_Type'] == 'Oil-Based') & (df['Completion_Type'] == 'Perforated')

df['Invalid_Combination'] = cond1 | cond2 | cond3 | cond4

# Calculate the percentage of suspicious data
invalid_count = df['Invalid_Combination'].sum()
invalid_percentage = invalid_count / len(df) * 100
print(f"Percentage of invalid combinations: {invalid_percentage:.2f}%")

# Decision based on percentage
if invalid_percentage < 1:
    print("Invalid combinations are less than 1%, ignoring the issue.")
    df_cleaned = df.drop(columns=["Invalid_Combination"])

elif 1 <= invalid_percentage < 5:
    print("Invalid combinations are between 1% and 5%, removing invalid rows.")
    df_cleaned = df[~df['Invalid_Combination']].drop(columns=["Invalid_Combination"])
    print(f"Removed {invalid_count} invalid rows.")

elif 5 <= invalid_percentage < 10:
    print("Invalid combinations are between 5% and 10%, further investigation recommended.")
    df[df['Invalid_Combination']].to_csv("invalid_rows.csv", index=False)
    print("[INFO] Invalid rows saved for further investigation.")
    df_cleaned = df.drop(columns=["Invalid_Combination"])

else:
    print("Invalid combinations are more than 10%, reconsider data collection process.")
    df[df['Invalid_Combination']].to_csv("invalid_rows.csv", index=False)
    print("[WARNING] Large number of invalid rows saved for auditing.")
    df_cleaned = df.drop(columns=["Invalid_Combination"])

# Save the cleaned data to local file
df_cleaned.to_parquet("formation_damage_valid_data.parquet", index=False)
print("[SUCCESS] Cleaned data saved to 'formation_damage_valid_data.parquet'")
