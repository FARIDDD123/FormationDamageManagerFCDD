import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.stats import skewnorm, gamma, pearsonr
from datetime import datetime, timedelta
import random
from faker import Faker
from tqdm import tqdm
import numba
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
NUM_NORMAL_RECORDS = 10_000_000
NUM_ABNORMAL_RECORDS = 500_000
FORMATION_TYPES = ['Haynesville Shale', 'Eagle Ford Shale', 'Permian Wolfcamp']
WELL_TYPES = ['Vertical', 'Horizontal', 'Deviated']
DAMAGE_TYPES = [
    'Clay Swelling', 'Iron Precipitation', 'Fluid Loss', 'Scale Formation',
    'Emulsion Blockage', 'Wettability Alteration', 'Fines Migration',
    'Organic Deposition', 'Mechanical Damage', 'Thermal Shock'
]

# Physical constants
API_TO_SG = 141.5 / 131.5  # API gravity to specific gravity conversion
PSI_TO_PA = 6894.76
FT_TO_M = 0.3048
CP_TO_PAS = 0.001
MD_TO_M2 = 9.86923e-16

@numba.jit(nopython=True)
def darcy_velocity(k_md, μ_cp, ΔP_psi, L_ft, A=1.0):
    """Calculate Darcy flow velocity with proper unit conversions"""
    k_m2 = k_md * MD_TO_M2
    μ_Pas = μ_cp * CP_TO_PAS
    ΔP_Pa = ΔP_psi * PSI_TO_PA
    L_m = L_ft * FT_TO_M
    return (k_m2 * A * ΔP_Pa) / (μ_Pas * L_m)

@numba.jit(nopython=True)
def moody_friction_factor(Re, ε_D=0.0001):
    """Improved Moody friction factor with roughness consideration"""
    if Re < 2000:
        return 64 / Re
    elif Re < 4000:
        # Transition zone
        return 0.032 + (0.021 - 0.032) * (Re - 2000) / 2000
    else:
        # Colebrook-White approximation
        f = 0.25 / (math.log10(ε_D/3.7 + 5.74/Re**0.9))**2
        return f

class AdvancedFormationModel:
    """Advanced physical model for formation properties"""
    
    def __init__(self, formation_type):
        self.formation = formation_type
        self.setup_formation_properties()
        
    def setup_formation_properties(self):
        """Initialize formation-specific parameters"""
        if self.formation == 'Haynesville Shale':
            self.depth_range = (10000, 14000)  # ft
            self.temp_gradient = 0.011  # °F/ft
            self.pressure_gradient = 0.47  # psi/ft
            self.clay_range = (0.15, 0.35)
            self.perm_range = (0.0001, 0.01)  # md
            self.porosity_range = (0.05, 0.12)
            self.tortuosity = 1.8
            self.cementation_factor = 2.2
            
        elif self.formation == 'Eagle Ford Shale':
            self.depth_range = (8000, 12000)
            self.temp_gradient = 0.0095
            self.pressure_gradient = 0.45
            self.clay_range = (0.1, 0.25)
            self.perm_range = (0.001, 0.1)
            self.porosity_range = (0.08, 0.15)
            self.tortuosity = 1.6
            self.cementation_factor = 2.0
            
        else:  # Permian Wolfcamp
            self.depth_range = (7000, 11000)
            self.temp_gradient = 0.0085
            self.pressure_gradient = 0.43
            self.clay_range = (0.05, 0.2)
            self.perm_range = (0.01, 1.0)
            self.porosity_range = (0.1, 0.18)
            self.tortuosity = 1.4
            self.cementation_factor = 1.8
    
    def generate_formation_params(self, is_abnormal):
        """Generate physically consistent formation parameters"""
        depth = np.random.uniform(*self.depth_range)
        
        # Temperature with random fluctuation
        temp = (depth * self.temp_gradient * (1 + random.uniform(-0.05, 0.05)))
        
        # Pressure with overpressure possibility
        if random.random() < 0.12:  # 12% chance of overpressure
            pressure = depth * self.pressure_gradient * random.uniform(1.1, 1.3)
        else:
            pressure = depth * self.pressure_gradient * random.uniform(0.95, 1.05)
        
        # Petrophysical properties with correlations
        clay = np.random.uniform(*self.clay_range)
        porosity = np.random.uniform(*self.porosity_range)
        
        # Permeability using modified Carman-Kozeny equation
        perm = (porosity**self.cementation_factor / 
               (self.tortuosity**2 * (1-porosity)**2)) * \
              10**(4*clay-2) * 1000  # Convert to md
        perm = np.clip(perm, *self.perm_range)
        
        # Introduce abnormalities if needed
        if is_abnormal:
            temp *= random.uniform(1.1, 1.4)
            pressure *= random.uniform(0.7, 1.6)
            perm *= random.uniform(0.01, 0.3)
            clay = min(clay * random.uniform(1.3, 2.5), 0.5)
            porosity *= random.uniform(0.8, 1.2)
        
        return {
            'depth_ft': depth,
            'temperature_f': temp,
            'pressure_psi': pressure,
            'clay_content': clay,
            'porosity': porosity,
            'permeability_md': perm,
            'tortuosity': self.tortuosity,
            'cementation_factor': self.cementation_factor
        }

def generate_fluid_properties(formation_params, is_abnormal):
    """Generate realistic fluid properties with advanced correlations"""
    # Base fluid properties
    api_gravity = np.random.uniform(20, 45)
    density_ppg = (141.5 / (api_gravity + 131.5)) * 8.33 * 1.3  # Convert API to ppg
    
    # Viscosity based on temperature and API
    temp_c = (formation_params['temperature_f'] - 32) * 5/9
    viscosity_cp = 10**(0.5 * (api_gravity / temp_c) - 1.5) * 100
    
    # pH based on formation and salinity
    salinity = 5000 + 245000 * formation_params['clay_content']
    ph = 6.5 + 4 * (1 - formation_params['clay_content']) + random.uniform(-0.5, 0.5)
    
    # Add realistic noise
    viscosity_cp *= random.uniform(0.9, 1.1)
    ph = np.clip(ph + random.uniform(-0.3, 0.3), 4, 11)
    
    # Abnormal fluid properties
    if is_abnormal:
        density_ppg *= random.uniform(0.8, 1.3)
        viscosity_cp *= random.uniform(1.5, 6)
        ph += random.uniform(-1.5, 1.5)
        salinity *= random.uniform(0.4, 2.2)
    
    return {
        'fluid_api': api_gravity,
        'fluid_density_ppg': density_ppg,
        'fluid_viscosity_cp': viscosity_cp,
        'ph': np.clip(ph, 3.5, 11.5),
        'salinity_ppm': salinity,
        'oil_water_ratio': random.uniform(0.7, 0.95)
    }

def generate_operational_parameters(formation_params, fluid_props, is_abnormal):
    """Generate realistic operational parameters with engineering constraints"""
    # Drilling parameters
    rpm = np.random.uniform(40, 160)
    wob = 5000 + 25000 * (formation_params['depth_ft'] / 14000)
    flow_rate = 200 + 600 * (formation_params['permeability_md'] / 1.0)
    
    # Calculate ECD with proper hydraulic model
    annular_velocity = flow_rate / (math.pi * (8.5**2 - 4.5**2) / 4 * 7.48052)  # gpm to ft/s
    ecd = fluid_props['fluid_density_ppg'] + \
          (annular_velocity * fluid_props['fluid_viscosity_cp'] * 0.000668) / \
          (formation_params['permeability_md']**0.2)
    
    # Calculate Reynolds number
    pipe_diameter = 4.5 / 12  # ft
    Re = (fluid_props['fluid_density_ppg'] * 119.8 * annular_velocity * pipe_diameter) / \
         (fluid_props['fluid_viscosity_cp'] * 0.000672)
    
    # Abnormal operations
    if is_abnormal:
        rpm *= random.uniform(0.4, 1.8)
        wob *= random.uniform(0.6, 1.7)
        flow_rate *= random.uniform(0.3, 2.5)
        ecd *= random.uniform(0.7, 1.6)
        Re *= random.uniform(0.5, 2.0)
    
    return {
        'rpm': rpm,
        'wob_lbs': wob,
        'flow_rate_gpm': flow_rate,
        'ecd_ppg': ecd,
        'reynolds_number': Re,
        'moody_friction': moody_friction_factor(Re)
    }

def calculate_damage_potential(params):
    """Advanced damage potential calculation with physical thresholds"""
    damage_type = None
    damage_score = 0
    
    # Clay swelling potential
    clay_risk = max(0, (params['clay_content'] - 0.2) / 0.3)  # پرانتز اضافه شد
    ph_effect = max(0, (7.5 - params['ph']) / 3.5) if params['ph'] < 7.5 else 0  # پرانتز اضافه شد
    clay_score = clay_risk * ph_effect
    
    # Scaling potential
    scaling_score = (params['salinity_ppm'] / 300000) * \
                   max(0, (params['ph'] - 8) / 2) if params['ph'] > 8 else 0  # پرانتز اضافه شد
    
    # بقیه کد بدون تغییر...
    
    # Emulsion potential
    emulsion_score = min(1, params['fluid_viscosity_cp'] / 100) * \
                    (1 - params['oil_water_ratio'])
    
    # Mechanical damage
    overbalance = params['ecd_ppg'] - (params['pressure_psi'] / (0.052 * params['depth_ft']))
    mech_score = max(0, overbalance / 2)
    
    # Determine primary damage type
    max_score = max(clay_score, scaling_score, emulsion_score, mech_score)
    if max_score > 0.3:  # Damage threshold
        if clay_score == max_score:
            damage_type = 'Clay Swelling'
        elif scaling_score == max_score:
            damage_type = 'Scale Formation'
        elif emulsion_score == max_score:
            damage_type = 'Emulsion Blockage'
        else:
            damage_type = 'Mechanical Damage'
    
    return damage_type, max_score

def generate_complete_record(formation_type, is_abnormal):
    """Generate one complete well record with all parameters"""
    formation_model = AdvancedFormationModel(formation_type)
    
    # Generate parameters
    formation_params = formation_model.generate_formation_params(is_abnormal)
    fluid_props = generate_fluid_properties(formation_params, is_abnormal)
    ops_params = generate_operational_parameters(formation_params, fluid_props, is_abnormal)
    
    # Combine all parameters
    record = {
        'well_id': f"{formation_type[:3]}-{random.randint(1000, 9999)}",
        'formation': formation_type,
        'well_type': random.choice(WELL_TYPES),
        'timestamp': datetime.now() - timedelta(days=random.randint(0, 365*5)),
        'is_abnormal': is_abnormal,
        **formation_params,
        **fluid_props,
        **ops_params
    }
    
    # Calculate damage potential
    damage_type, damage_score = calculate_damage_potential(record)
    record.update({
        'damage_type': damage_type,
        'damage_score': damage_score,
        'darcy_velocity': darcy_velocity(
            record['permeability_md'],
            record['fluid_viscosity_cp'],
            record['pressure_psi'],
            record['depth_ft']
        )
    })
    
    return record

def generate_batch(batch_size, formation_types, abnormal_ratio=0.0):
    """Generate a batch of records with specified abnormal ratio"""
    records = []
    for _ in range(batch_size):
        formation = random.choice(formation_types)
        is_abnormal = random.random() < abnormal_ratio
        records.append(generate_complete_record(formation, is_abnormal))
    return records

def generate_dataset(num_normal, num_abnormal, batch_size=10000):
    """Generate full dataset using parallel processing"""
    records = []
    formation_types = FORMATION_TYPES
    
    # Calculate ratios for batch processing
    total_records = num_normal + num_abnormal
    abnormal_ratio = num_abnormal / total_records
    
    # Generate in parallel batches
    with ThreadPoolExecutor() as executor:
        futures = []
        batches = (total_records // batch_size) + 1
        
        for _ in tqdm(range(batches), desc="Scheduling batches"):
            futures.append(executor.submit(
                generate_batch,
                min(batch_size, total_records - len(records)),
                formation_types,
                abnormal_ratio
            ))
        
        for future in tqdm(as_completed(futures), desc="Processing batches"):
            records.extend(future.result())
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Ensure exact counts
    normal_df = df[~df['is_abnormal']].head(num_normal)
    abnormal_df = df[df['is_abnormal']].head(num_abnormal)
    final_df = pd.concat([normal_df, abnormal_df]).sample(frac=1).reset_index(drop=True)
    
    return final_df

def save_to_parquet(df, filename):
    """Save optimized Parquet file with partitioning"""
    table = pa.Table.from_pandas(df)
    
    # Use advanced compression and encoding
    pq.write_table(
        table,
        filename,
        compression='ZSTD',
        use_dictionary=['formation', 'well_type', 'damage_type'],
        version='2.6',
        data_page_size=1_000_000  # Optimize for large files
    )

def main():
    print(f"Generating dataset with {NUM_NORMAL_RECORDS:,} normal and {NUM_ABNORMAL_RECORDS:,} abnormal records...")
    
    # Generate dataset
    df = generate_dataset(NUM_NORMAL_RECORDS, NUM_ABNORMAL_RECORDS)
    
    # Save to Parquet
    output_file = 'industrial_formation_damage_data.parquet'
    save_to_parquet(df, output_file)
    
    # Print summary
    print("\nDataset summary:")
    print(f"Total records: {len(df):,}")
    print(f"Normal records: {len(df[~df['is_abnormal']]):,}")
    print(f"Abnormal records: {len(df[df['is_abnormal']]):,}")
    print("\nDamage type distribution:")
    print(df['damage_type'].value_counts(dropna=False))
    print("\nFormation distribution:")
    print(df['formation'].value_counts())

if __name__ == "__main__":
    main()