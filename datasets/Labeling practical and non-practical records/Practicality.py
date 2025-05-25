import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from datetime import datetime
<<<<<<< HEAD
import glob
import os

# Configuration
INPUT_DIR = "/content/drive/MyDrive/project ifdc-fcw/dataset"
OUTPUT_DIR = "/content/drive/MyDrive/project ifdc-fcw/practicality/processed_results"
REPORT_DIR = "/content/drive/MyDrive/project ifdc-fcw/practicality/analysis_reports"
FILE_PATTERN = "Haynesville_*.parquet"

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
=======

# Configuration
INPUT_FILE = "formation_damage_dataset.parquet"
OUTPUT_FILE = "formation_damage_with_practicality.parquet"
REPORT_FILE = "practicality_report.pdf"
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4

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
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 2. Drilling Damage
    "Drilling_Damage": {
        "overbalance": (200, 500),  # psi
        "rop": (12, 22),  # ft/hr
        "wob": (8000, 20000),  # lbs
        "mud_viscosity": (40, 50),  # cP
        "gel_strength": (8, 15),  # lb/100ft²
        "flow_rate": (600, 1000)  # gpm
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 3. Fluid Loss
    "Fluid_Loss": {
        "permeability": (80, 300),  # mD
        "mud_weight": (11.0, 13.0),  # ppg
        "yp": (15, 25),  # lb/100ft²
<<<<<<< HEAD
       
    },

=======
        "fluid_loss": (0, 10),  # cc/30min
        "filter_cake": (2, 4)  # mm/32in
    },
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 4. Fluid Incompatibility
    "Fluid_Incompatibility": {
        "ph": (7.0, 8.0),
        "temperature": (130, 170),  # °F
        "salinity_diff": (0, 5000),  # ppm difference
        "hardness": (0, 200),  # mg/L as CaCO3
        "scale_tendency": (0, 0.3),  # saturation index
        "sludge_potential": (0, 0.5)  # sludge index
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 5. Near-Wellbore Emulsions
    "Near_Wellbore_Emulsions": {
        "water_cut": (10, 60),  # %
        "oil_viscosity": (20, 100),  # cP
        "surfactant_concentration": (0.1, 0.5),  # %
        "shear_rate": (100, 500),  # 1/s
        "interfacial_tension": (1, 10)  # dynes/cm
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 6. Rock/Fluid Interactions
    "Rock_Fluid_Interactions": {
        "clay_reactivity": (0, 0.7),  # reactivity index
        "brittleness_index": (0.4, 0.8),
        "water_sensitivity": (0, 0.6),
        "velocity_sensitivity": (0, 0.5),
        "ion_exchange": (0, 0.4)  # meq/100g
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 7. Completion Connectivity
    "Completion_Connectivity": {
        "skin_factor": (-1, 5),
        "perforation_density": (6, 12),  # shots/ft
        "perforation_diameter": (0.3, 0.5),  # inch
        "frac_conductivity": (1000, 5000),  # md-ft
        "gravel_pack_permeability": (50, 200)  # Darcies
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 8. Cracking from Corrosion/Stress
    "Cracking_Corrosion_Stress": {
        "stress_ratio": (0.6, 0.9),
        "corrosion_rate": (0, 5),  # mpy
        "h2s_content": (0, 50),  # ppm
        "co2_partial_pressure": (0, 30),  # psi
        "chloride_content": (0, 50000)  # ppm
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 9. Surface Filtration
    "Surface_Filtration": {
        "particle_size_distribution": (10, 50),  # D50 in microns
        "solids_content": (0, 5),  # %
        "filter_mesh_size": (100, 200),  # mesh
        "turbidity": (0, 20),  # NTU
        "filter_cake_porosity": (20, 40)  # %
    },
<<<<<<< HEAD

=======
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    # 10. Ultra-Clean Fluids
    "Ultra_Clean_Fluids": {
        "solid_content": (0, 1),  # %
        "filterability": (90, 100),  # %
        "microbial_count": (0, 100),  # CFU/ml
        "oxygen_content": (0, 0.5),  # ppm
        "tss": (0, 10)  # mg/L
    }
}

<<<<<<< HEAD
=======
def load_data():
    """Load input data"""
    print("🔍 Loading data...")
    return pd.read_parquet(INPUT_FILE)

>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
def is_practical(row):
    """Determine if damage is practical based on rules"""
    if row['damage_type'] == 'No_Damage':
        return 'Non-Practical'
<<<<<<< HEAD

    if row['damage_type'] not in PRACTICALITY_RULES:
        return 'Non-Practical'

=======
    
    if row['damage_type'] not in PRACTICALITY_RULES:
        return 'Non-Practical'
    
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4
    rules = PRACTICALITY_RULES[row['damage_type']]
    for param, (min_val, max_val) in rules.items():
        if param in row and not (min_val <= row[param] <= max_val):
            return 'Non-Practical'
<<<<<<< HEAD

    return 'Practical'

def generate_report(df, report_path):
    """Generate PDF report for a single dataset"""
    try:
        with PdfPages(report_path) as pdf:
            # Title page
            plt.figure(figsize=(11, 8))
            plt.text(0.5, 0.6, 'Formation Damage Analysis Report',
                    ha='center', va='center', size=24, fontweight='bold')
            plt.text(0.5, 0.5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                              f"Records Processed: {len(df):,}\n"
                              f"File: {os.path.basename(report_path)}",
                    ha='center', va='center', size=14)
            plt.axis('off')
            pdf.savefig()
            plt.close()

            # Summary statistics
            plt.figure(figsize=(10, 6))
            practical_count = (df['damage_practicality'] == 'Practical').sum()
            labels = ['Practical', 'Non-Practical']
            sizes = [practical_count, len(df) - practical_count]
            plt.pie(sizes, labels=labels, autopct='%1.1f%%',
                   colors=['#4CAF50', '#F44336'])
            plt.title('Damage Practicality Distribution')
            pdf.savefig()
            plt.close()

            # Damage type distribution
            plt.figure(figsize=(10, 6))
            damage_counts = df['damage_type'].value_counts()
            damage_counts.plot(kind='bar', color='skyblue')
            plt.title('Damage Type Distribution')
            plt.xlabel('Damage Type')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            pdf.savefig()
            plt.close()

            # Parameter distributions (example for 3 key parameters)
            for param in ['ph', 'temperature', 'pressure'][:3]:
                if param in df.columns:
                    plt.figure(figsize=(10, 6))
                    sns.histplot(data=df, x=param, hue='damage_practicality',
                                bins=20, kde=True, palette=['#4CAF50', '#F44336'])
                    plt.title(f'{param.capitalize()} Distribution')
                    pdf.savefig()
                    plt.close()

            # Sample data tables
            plt.figure(figsize=(11, 8))
            plt.text(0.1, 0.9, 'Sample Practical Records:', size=14)
            sample_df = df[df['damage_practicality'] == 'Practical'].head(3)
            plt.table(cellText=sample_df.values,
                     colLabels=sample_df.columns,
                     loc='center')
            plt.axis('off')
            pdf.savefig()
            plt.close()

        print(f"   Successfully generated report: {report_path}")
        return True
    except Exception as e:
        print(f"   Error generating report: {str(e)}")
        return False

def process_single_file(input_path):
    """Process a single input file"""
    try:
        base_name = os.path.basename(input_path).replace('.parquet', '')
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_processed.parquet")
        report_path = os.path.join(REPORT_DIR, f"{base_name}_report.pdf")

        print(f"\nProcessing: {input_path}")

        # Load and process data
        df = pd.read_parquet(input_path)
        df['damage_practicality'] = df.apply(is_practical, axis=1)

        # Save outputs
        df.to_parquet(output_path)
        print(f"  Saved processed data to: {output_path}")

        # Generate report
        if generate_report(df, report_path):
            return True
        return False

    except Exception as e:
        print(f"  Error processing file: {str(e)}")
        return False

def main():
    print("Starting Formation Damage Analysis Pipeline")
    print("=========================================")

    # Find all input files
    input_files = glob.glob(os.path.join(INPUT_DIR, FILE_PATTERN))
    if not input_files:
        print(f"No files found matching: {FILE_PATTERN} in {INPUT_DIR}")
        return

    print(f"Found {len(input_files)} files to process")

    # Process each file
    success_count = 0
    for file in input_files:
        if process_single_file(file):
            success_count += 1

    print("\nProcessing Summary:")
    print(f"Successfully processed: {success_count}/{len(input_files)} files")
    print(f"Processed data saved to: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Analysis reports saved to: {os.path.abspath(REPORT_DIR)}")
=======
    
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
>>>>>>> f6429b84b2bdcf27019d30218a62b04657d1dbb4

if __name__ == "__main__":
    main()