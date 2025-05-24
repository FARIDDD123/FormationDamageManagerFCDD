import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from datetime import datetime

# Configuration
INPUT_FILE = "formation_damage_dataset.parquet"
OUTPUT_FILE = "formation_damage_with_practicality.parquet"
REPORT_FILE = "practicality_report.pdf"

# Operational rules for all 10 damage types
PRACTICALITY_RULES = {
    # 1. Clay & Iron Control
    "Clay_Iron_Control": {
        "ph": (6.5, 8.5),
        "temperature": (120, 160),  # °F
        "salinity": (15000, 35000),  # ppm
        "clay_content": (5, 25),  # %
        "iron_content": (0.5, 3.0),  # %
        "mud_weight": (10.5, 12.5),  # ppg
        "lime_content": (1, 3)  # lb/bbl
    },
    
    # 2. Drilling Damage
    "Drilling_Damage": {
        "overbalance": (200, 500),  # psi
        "rop": (12, 22),  # ft/hr
        "wob": (8000, 20000),  # lbs
        "mud_viscosity": (40, 50),  # cP
        "gel_strength": (8, 15),  # lb/100ft²
        "flow_rate": (600, 1000)  # gpm
    },
    
    # 3. Fluid Loss
    "Fluid_Loss": {
        "permeability": (80, 300),  # mD
        "mud_weight": (11.0, 13.0),  # ppg
        "yp": (15, 25),  # lb/100ft²
        "fluid_loss": (0, 10),  # cc/30min
        "filter_cake": (2, 4)  # mm/32in
    },
    
    # 4. Fluid Incompatibility
    "Fluid_Incompatibility": {
        "ph": (7.0, 8.0),
        "temperature": (130, 170),  # °F
        "salinity_diff": (0, 5000),  # ppm difference
        "hardness": (0, 200),  # mg/L as CaCO3
        "scale_tendency": (0, 0.3),  # saturation index
        "sludge_potential": (0, 0.5)  # sludge index
    },
    
    # 5. Near-Wellbore Emulsions
    "Near_Wellbore_Emulsions": {
        "water_cut": (10, 60),  # %
        "oil_viscosity": (20, 100),  # cP
        "surfactant_concentration": (0.1, 0.5),  # %
        "shear_rate": (100, 500),  # 1/s
        "interfacial_tension": (1, 10)  # dynes/cm
    },
    
    # 6. Rock/Fluid Interactions
    "Rock_Fluid_Interactions": {
        "clay_reactivity": (0, 0.7),  # reactivity index
        "brittleness_index": (0.4, 0.8),
        "water_sensitivity": (0, 0.6),
        "velocity_sensitivity": (0, 0.5),
        "ion_exchange": (0, 0.4)  # meq/100g
    },
    
    # 7. Completion Connectivity
    "Completion_Connectivity": {
        "skin_factor": (-1, 5),
        "perforation_density": (6, 12),  # shots/ft
        "perforation_diameter": (0.3, 0.5),  # inch
        "frac_conductivity": (1000, 5000),  # md-ft
        "gravel_pack_permeability": (50, 200)  # Darcies
    },
    
    # 8. Cracking from Corrosion/Stress
    "Cracking_Corrosion_Stress": {
        "stress_ratio": (0.6, 0.9),
        "corrosion_rate": (0, 5),  # mpy
        "h2s_content": (0, 50),  # ppm
        "co2_partial_pressure": (0, 30),  # psi
        "chloride_content": (0, 50000)  # ppm
    },
    
    # 9. Surface Filtration
    "Surface_Filtration": {
        "particle_size_distribution": (10, 50),  # D50 in microns
        "solids_content": (0, 5),  # %
        "filter_mesh_size": (100, 200),  # mesh
        "turbidity": (0, 20),  # NTU
        "filter_cake_porosity": (20, 40)  # %
    },
    
    # 10. Ultra-Clean Fluids
    "Ultra_Clean_Fluids": {
        "solid_content": (0, 1),  # %
        "filterability": (90, 100),  # %
        "microbial_count": (0, 100),  # CFU/ml
        "oxygen_content": (0, 0.5),  # ppm
        "tss": (0, 10)  # mg/L
    }
}

def load_data():
    """Load input data"""
    print("🔍 Loading data...")
    return pd.read_parquet(INPUT_FILE)

def is_practical(row):
    """Determine if damage is practical based on rules"""
    if row['damage_type'] == 'No_Damage':
        return 'Non-Practical'
    
    if row['damage_type'] not in PRACTICALITY_RULES:
        return 'Non-Practical'
    
    rules = PRACTICALITY_RULES[row['damage_type']]
    for param, (min_val, max_val) in rules.items():
        if param in row and not (min_val <= row[param] <= max_val):
            return 'Non-Practical'
    
    return 'Practical'

def process_data(df):
    """Process data and add practicality labels"""
    print("⚙️ Processing data and labeling...")
    df['damage_practicality'] = df.apply(is_practical, axis=1)
    return df

def generate_report(df):
    """Generate PDF report"""
    print("📊 Generating analysis report...")
    
    with PdfPages(REPORT_FILE) as pdf:
        # Title page
        plt.figure(figsize=(11, 8))
        plt.text(0.5, 0.6, 'Formation Damage Practicality Analysis Report', 
                ha='center', va='center', size=24, fontweight='bold')
        plt.text(0.5, 0.5, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n\n'
                          'Oil & Gas Well Damage Management System',
                ha='center', va='center', size=16)
        plt.axis('off')
        pdf.savefig()
        plt.close()

        # Executive summary
        plt.figure(figsize=(11, 8))
        total_records = len(df)
        practical_count = len(df[df['damage_practicality'] == 'Practical'])
        practical_percent = (practical_count / total_records) * 100
        
        summary_text = [
            f"Total records: {total_records:,}",
            f"Practical records: {practical_count:,} ({practical_percent:.1f}%)",
            f"Non-Practical records: {total_records - practical_count:,} ({100 - practical_percent:.1f}%)",
            "\nPractical damage type distribution:"
        ]
        
        practical_df = df[df['damage_practicality'] == 'Practical']
        if not practical_df.empty:
            damage_dist = practical_df['damage_type'].value_counts()
            for damage_type, count in damage_dist.items():
                summary_text.append(f"- {damage_type}: {count} records ({count/practical_count*100:.1f}%)")
        
        plt.text(0.1, 0.9, '\n'.join(summary_text), size=12, ha='left', va='top')
        plt.axis('off')
        pdf.savefig()
        plt.close()

        # Overall distribution chart
        plt.figure(figsize=(10, 6))
        df['damage_practicality'].value_counts().plot(
            kind='pie', 
            autopct='%1.1f%%', 
            colors=['#4CAF50', '#F44336'],
            textprops={'fontsize': 12}
        )
        plt.title('Overall Practical vs Non-Practical Distribution', fontsize=14)
        pdf.savefig()
        plt.close()

        # Analysis by damage type
        for damage_type in df['damage_type'].unique():
            if damage_type == 'No_Damage':
                continue
                
            subset = df[df['damage_type'] == damage_type]
            if len(subset) == 0:
                continue
            
            # Practicality distribution for this damage type
            plt.figure(figsize=(10, 6))
            subset['damage_practicality'].value_counts().plot(
                kind='bar', 
                color=['#4CAF50', '#F44336'],
                rot=0
            )
            plt.title(f'Practicality Distribution for {damage_type}', fontsize=14)
            plt.xlabel('')
            plt.ylabel('Record Count')
            pdf.savefig()
            plt.close()
            
            # Key parameter histograms
            if damage_type in PRACTICALITY_RULES:
                params = list(PRACTICALITY_RULES[damage_type].keys())[:3]  # Show first 3 parameters
                for param in params:
                    if param in df.columns:
                        plt.figure(figsize=(10, 6))
                        sns.histplot(
                            data=subset, 
                            x=param, 
                            hue='damage_practicality',
                            bins=20, 
                            kde=True,
                            palette=['#4CAF50', '#F44336']
                        )
                        plt.title(f'{param} Distribution for {damage_type}', fontsize=14)
                        pdf.savefig()
                        plt.close()

        # Data samples
        plt.figure(figsize=(11, 8))
        plt.text(0.1, 0.9, 'Sample Practical Records:', size=14, fontweight='bold')
        sample_practical = df[df['damage_practicality'] == 'Practical'].sample(3)
        plt.table(
            cellText=sample_practical.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            colWidths=[0.1]*len(df.columns)
        )
        plt.axis('off')
        pdf.savefig()
        plt.close()
        
        plt.figure(figsize=(11, 8))
        plt.text(0.1, 0.9, 'Sample Non-Practical Records:', size=14, fontweight='bold')
        sample_non_practical = df[df['damage_practicality'] == 'Non-Practical'].sample(3)
        plt.table(
            cellText=sample_non_practical.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            colWidths=[0.1]*len(df.columns))
        plt.axis('off')
        pdf.savefig()
        plt.close()

        # Closing page
        plt.figure(figsize=(11, 8))
        plt.text(0.5, 0.5, 'End of Report\n\nFormation Damage Management System', 
                ha='center', va='center', size=16)
        plt.axis('off')
        pdf.savefig()
        plt.close()

def save_results(df):
    """Save processed results"""
    print("💾 Saving results...")
    df.to_parquet(OUTPUT_FILE, index=False)

def main():
    try:
        # Execute processing
        df = load_data()
        processed_df = process_data(df)
        
        # Save results
        save_results(processed_df)
        
        # Generate report
        generate_report(processed_df)
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📊 Results saved to '{OUTPUT_FILE}'")
        print(f"📄 Analysis report generated as '{REPORT_FILE}'")
        
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")

if __name__ == "__main__":
    main()