import pandas as pd
import numpy as np

np.random.seed(42)

n_wells = 10
n_rows_per_well = 15_552_000
chunk_size = 1_000_000  # اندازه چانک
start_time = pd.Timestamp("2023-01-01")

wells = [
    {"API_Well_ID": "40100050", "LONG": -94.86, "LAT": 32.26},
    {"API_Well_ID": "40131881", "LONG": -94.82, "LAT": 32.26},
    {"API_Well_ID": "40134068", "LONG": -94.78, "LAT": 32.25},
    {"API_Well_ID": "40181715", "LONG": -94.95, "LAT": 32.17},
    {"API_Well_ID": "36535068", "LONG": -94.18, "LAT": 32.32},
    {"API_Well_ID": "36500362", "LONG": -94.13, "LAT": 32.32},
    {"API_Well_ID": "36530944", "LONG": -94.15, "LAT": 32.12},
    {"API_Well_ID": "18332094", "LONG": -94.62, "LAT": 32.37},
    {"API_Well_ID": "18331921", "LONG": -94.6, "LAT": 32.37},
    {"API_Well_ID": "18387931", "LONG": -94.86, "LAT": 32.45}
]

formation_types = ['Sandstone', 'Limestone', 'Shale', 'Dolomite']
clay_types = ['Kaolinite', 'Illite', 'Smectite', 'Mixed Layer']
mud_types = ['Water-Based', 'Oil-Based', 'Synthetic-Based']
presence_of_fractures = ['Yes', 'No']

clip = lambda x, low, high: np.clip(x, low, high)

for well_id in range(n_wells):
    well = wells[well_id]
    well_api = well['API_Well_ID']
    well_long = well['LONG']
    well_lat = well['LAT']

    filename = f"formation_damage_well_{well_id+1}.parquet"
    first_chunk = True  # برای ذخیره‌سازی اولیه یا الحاق

    # پردازش در چانک‌های کوچکتر
    for chunk_start in range(0, n_rows_per_well, chunk_size):
        chunk_end = min(chunk_start + chunk_size, n_rows_per_well)
        chunk_len = chunk_end - chunk_start

        time_deltas = pd.to_timedelta(np.arange(chunk_start, chunk_end), unit='s')
        df = pd.DataFrame({
            'API_Well_ID': well_api,
            'DateTime': start_time + time_deltas,
            'LAT': well_lat,
            'LONG': well_long,
            'Measured_Depth': np.linspace(5000, 12000, n_rows_per_well)[chunk_start:chunk_end] + np.random.normal(0, 10, chunk_len),
            'Bit_Depth': np.linspace(5000, 12000, n_rows_per_well)[chunk_start:chunk_end] + np.random.normal(0, 10, chunk_len),
            'WOB': clip(np.random.normal(25, 5, chunk_len), 10, 50),
            'RPM': clip(np.random.normal(120, 20, chunk_len), 60, 200),
            'ROP': clip(np.random.normal(45, 15, chunk_len), 10, 100),
            'Torque': clip(np.random.normal(900, 100, chunk_len), 600, 1200),
            'Standpipe_Pressure': clip(np.random.normal(3000, 300, chunk_len), 2000, 4000),
            'Annulus_Pressure': clip(np.random.normal(2500, 250, chunk_len), 1500, 3500),
            'Reservoir_Pressure': clip(np.random.normal(4500, 300, chunk_len), 3000, 6000),
            'Pore_Pressure_psi': clip(np.random.normal(4000, 300, chunk_len), 2500, 5500),
            'Overbalance': np.nan,
            'Formation_Type': np.random.choice(formation_types, chunk_len),
            'Formation_Permeability': clip(np.random.lognormal(mean=2, sigma=0.8, size=chunk_len), 0.1, 1000),
            'Reservoir_Temperature': clip(np.random.normal(100, 10, chunk_len), 70, 150),
            'Clay_Content_Percent': clip(np.random.normal(20, 10, chunk_len), 0, 50),
            'Clay_Mineralogy_Type': np.random.choice(clay_types, chunk_len),
            'Shale_Reactiveness': clip(np.random.normal(0.5, 0.2, chunk_len), 0, 1),
            'Presence_of_Fractures': np.random.choice(presence_of_fractures, chunk_len),
            'Mud_Type': np.random.choice(mud_types, chunk_len),
            'Mud_pH': clip(np.random.normal(8.5, 0.5, chunk_len), 7.0, 10.5),
            'Mud_Weight_In': clip(np.random.normal(9.5, 1, chunk_len), 8.0, 12.5),
            'Mud_Flow_Rate_In': clip(np.random.normal(500, 100, chunk_len), 300, 800),
            'Mud_Flow_Rate_Out': clip(np.random.normal(495, 100, chunk_len), 290, 800),
            'Mud_Temperature_In': clip(np.random.normal(75, 5, chunk_len), 60, 90),
            'Mud_Temperature_Out': clip(np.random.normal(85, 5, chunk_len), 70, 100),
            'Chloride_Content': clip(np.random.normal(18000, 2000, chunk_len), 10000, 25000),
            'Solid_Content': clip(np.random.normal(5, 2, chunk_len), 0, 15),
            'Oil_Water_Ratio': clip(np.random.normal(70, 10, chunk_len), 50, 90),
            'Pit_Volume': clip(np.random.normal(800, 50, chunk_len), 700, 900),
            'Viscosity': clip(np.random.normal(35, 10, chunk_len), 20, 60),
            'Fluid_Loss_API': clip(np.random.normal(6, 3, chunk_len), 2, 15),
            'Young_Modulus_GPa': clip(np.random.normal(25, 5, chunk_len), 10, 40),
            'Poisson_Ratio': clip(np.random.normal(0.25, 0.05, chunk_len), 0.1, 0.4),
            'Brittleness_Index': clip(np.random.normal(0.5, 0.15, chunk_len), 0, 1),
            'Formation_Damage_Index': np.nan,
            'Clay_Damage_Index': np.nan,
            'Emulsion_Risk_Index': np.nan,
            'Fluid_Loss_Risk_Index': np.nan,
            'Rock_Fluid_Interaction_Risk_Index': np.nan
        })

        df['Overbalance'] = df['Standpipe_Pressure'] - df['Pore_Pressure_psi']

        df['Clay_Damage_Index'] = clip((df['Clay_Content_Percent'] / 50) * (10 - df['Mud_pH']) * (df['Chloride_Content'] / 20000), 0, 1)
        df['Emulsion_Risk_Index'] = clip((df['Oil_Water_Ratio'] / 100) * (df['Solid_Content'] / 10), 0, 1)
        df['Fluid_Loss_Risk_Index'] = clip(df['Fluid_Loss_API'] / 15, 0, 1)
        df['Rock_Fluid_Interaction_Risk_Index'] = clip((df['Shale_Reactiveness'] + (1 - df['Brittleness_Index'])) / 2, 0, 1)

        df['Formation_Damage_Index'] = clip(
            0.25 * df['Clay_Damage_Index'] +
            0.2 * df['Emulsion_Risk_Index'] +
            0.25 * df['Fluid_Loss_Risk_Index'] +
            0.3 * df['Rock_Fluid_Interaction_Risk_Index'], 0, 1
        )

        # ذخیره به صورت الحاقی
        if first_chunk:
            df.to_parquet(filename, index=False)
            first_chunk = False
        else:
            # پارکت امکان append مستقیم ندارد، پس باید راه‌حل زیر را استفاده کنیم:
            # ۱) بارگذاری فایل قبلی
            # ۲) اضافه کردن داده جدید به آن
            # ۳) ذخیره مجدد (اگر حجم خیلی بزرگ بود، باید از دیتابیس یا فرمت دیگری استفاده کنید)
            old_df = pd.read_parquet(filename)
            combined_df = pd.concat([old_df, df], ignore_index=True)
            combined_df.to_parquet(filename, index=False)
        print(f"Added chunk rows {chunk_start} to {chunk_end} for well {well_api}")
    print(f"Saved {filename} for well {well_api}")
