
import pandas as pd
import re

# 1. Reading the normalized data from Task 4
df = pd.read_parquet('formation_damage_normalized.parquet')

# 2. List of target text columns (based on the synthetic dataset)
text_columns = ['Formation', 'Fluid_Type', 'Completion_Type', 'Damage_Type']

# 3. Text normalization function with expanded typo corrections
def clean_text(text):
    if pd.isna(text):
        return text
    text = str(text)
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    text = text.lower()  # Convert to lowercase
    
    # Expanding typo corrections
    typo_dict = {
        # General typos
        'flud': 'fluid',
        'cmp': 'completion',
        'formaiton': 'formation',
        'damge': 'damage',
        'fluied': 'fluid',
        'completon': 'completion',
        'typee': 'type',
        'compition': 'competition',
        'damaage': 'damage',
        'fludtype': 'fluid_type',
        'flud_typ': 'fluid_type',
        'completition': 'completion',
        'exmaple': 'example',
        
        # Common typos involving letters near each other on the keyboard
        'fliud': 'fluid',
        'flluid': 'fluid',
        'comp': 'completion',
        'cmpletion': 'completion',
        'damge': 'damage',
        'damge': 'damage',
        'comple': 'complete',
        
        # Misspellings of "formation"
        'formtion': 'formation',
        'fomration': 'formation',
        
        # Other general corrections
        'exmple': 'example',
        'occurance': 'occurrence',
        'recieve': 'receive',
        'definately': 'definitely',
        'untill': 'until',
        
        # Handling abbreviations
        'fl': 'fluid',
        'cmpn': 'completion',
        'ty': 'type',
        
        # Common mis-spellings in dataset names
        'completiontype': 'completion_type',
        'damagetype': 'damage_type',
        'fluidtype': 'fluid_type',
    }
    
    # Applying all typo corrections
    for typo, correct in typo_dict.items():
        text = text.replace(typo, correct)
    
    return text

# 4. Apply normalization on text columns
for col in text_columns:
    if col in df.columns:  # Check if the column exists in the dataframe
        df[col] = df[col].apply(clean_text)
    else:
        print(f"Column {col} does not exist in the dataframe!")

# 5. Save the normalized data to the new Parquet file
df.to_parquet('final_formation_damage_dataset.parquet', index=False)

# 6. Extract unique values and save them in a single parquet file
unique_data = {}
for col in text_columns:
    if col in df.columns:
        unique_data[col] = df[col].unique().tolist()

# Create a dataframe from unique values (filling unequal lengths with None)
max_length = max(len(values) for values in unique_data.values())
for col in unique_data:
    unique_data[col] += [None] * (max_length - len(unique_data[col]))

pd.DataFrame(unique_data).to_parquet('all_unique_values.parquet', index=False)

print("Processing complete!")
