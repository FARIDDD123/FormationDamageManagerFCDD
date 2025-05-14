import pandas as pd
import numpy as np
from pathlib import Path

# ======================= CONFIGURATION =======================
# File paths and processing parameters
INPUT_FILE = "formation_damage_optimized.parquet"
OUTLIERS_REPORT_FILE = "outliers_report.parquet"
CLEANED_DATA_FILE = "formation_damage_cleaned.parquet"
COLUMNS_TO_CHECK = ["Temperature_C", "Pressure_psi", "Permeability_mD", "Flow_Rate_bbl_day"]
ACTION = 'clip'  # Options: 'clip' (replace with bounds) or 'remove' (delete outliers)
IQR_THRESHOLD = 1.5  # Standard threshold for outlier detection

# ======================= OUTLIER DETECTION =======================
def detect_outliers_iqr(data, column, threshold=IQR_THRESHOLD):
    """Identify outliers using IQR method for a single column"""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - (threshold * IQR)
    upper_bound = Q3 + (threshold * IQR)
    
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)].copy()
    outliers['Bound_Type'] = np.where(outliers[column] < lower_bound, 'Lower', 'Upper')
    outliers['Bound_Value'] = np.where(outliers[column] < lower_bound, lower_bound, upper_bound)
    outliers['Feature'] = column
    
    return outliers, (lower_bound, upper_bound)

def generate_outliers_report(df, columns):
    """Generate comprehensive outlier report for all specified columns"""
    all_outliers = pd.DataFrame()
    bounds_info = {}
    
    for col in columns:
        outliers, bounds = detect_outliers_iqr(df, col)
        all_outliers = pd.concat([all_outliers, outliers])
        bounds_info[col] = bounds
    
    if not all_outliers.empty:
        all_outliers.to_parquet(OUTLIERS_REPORT_FILE, index=False)
        print(f"[SUCCESS] Outlier report saved to '{OUTLIERS_REPORT_FILE}'")
    
    return all_outliers, bounds_info

# ======================= DATA PROCESSING =======================
def handle_outliers(df, bounds_info, action=ACTION):
    """Process outliers by either clipping or removing them"""
    df_clean = df.copy()
    
    if action == 'clip':
        for col, bounds in bounds_info.items():
            df_clean[col] = df_clean[col].clip(lower=bounds[0], upper=bounds[1])
    elif action == 'remove':
        for col, bounds in bounds_info.items():
            mask = (df_clean[col] >= bounds[0]) & (df_clean[col] <= bounds[1])
            df_clean = df_clean[mask]
    
    # Maintain original data types for optimal storage
    df_clean = df_clean.astype({
        "Well_ID": "category",
        "Formation": "category",
        "Fluid_Type": "category",
        "Completion_Type": "category",
        "Damage_Type": "category"
    })
    
    df_clean.to_parquet(CLEANED_DATA_FILE, index=False)
    print(f"[SUCCESS] Cleaned dataset saved to '{CLEANED_DATA_FILE}'")
    
    return df_clean

# ======================= MAIN EXECUTION =======================
def main():
    """Main workflow execution"""    
    if not Path(INPUT_FILE).exists():
        print(f"[ERROR] Input file '{INPUT_FILE}' not found!")
        return
    
    df = pd.read_parquet(INPUT_FILE)
    print(f"\n[STATUS] Dataset loaded with {len(df):,} records")
    
    outliers_report, bounds_info = generate_outliers_report(df, COLUMNS_TO_CHECK)
    
    if not outliers_report.empty:
        df_clean = handle_outliers(df, bounds_info, action=ACTION)
        
        # Display sample changes
        sample = outliers_report.sample(min(3, len(outliers_report)))
        print("\n[SAMPLE CHANGES] Example modifications:")
        for idx, row in sample.iterrows():
            original = df.loc[idx, row['Feature']]
            cleaned = df_clean.loc[idx, row['Feature']]
            print(f"{row['Feature']} (Well {df.loc[idx, 'Well_ID']}):")
            print(f"  Original: {original:.2f} → Cleaned: {cleaned:.2f}")
            print(f"  {row['Bound_Type']} bound: {row['Bound_Value']:.2f}\n")
        
        print(f"\n[SUMMARY] Initial records: {len(df):,}")
        print(f"          Outliers detected: {len(outliers_report):,}")
        print(f"          Final records: {len(df_clean):,}")

if __name__ == "__main__":
    main()
