# Formation Damage Dataset Documentation

## 📌 Overview
This dataset contains synthetic formation damage data for oil and gas wells, optimized for machine learning tasks. It includes both normal operational data and abnormal scenarios.

## 📊 Dataset Specifications
- **Format**: Parquet (optimized for storage/processing)
- **Total Records**: 10,500,000 (10M normal + 500K abnormal)
- **Size**: ~2.1GB (compressed)
- **Final File Size**: **968.2MB**
- **Data Types**:
  - Numerical: float32
  - Categorical: category (optimized)
- **Missing Values**: 5% of salinity data (for imputation tasks)


## 🏗️ Data Generation Details
### Normal Data (10M records)
- Temperature: 50-200°C
- Pressure: 1,000-15,000 psi
- pH: 3.5-9.0
- Randomly distributed damage types

### Abnormal Data (500K records)
- Extreme values outside normal ranges
- Focused on critical damage types:
  - Corrosion Cracking
  - Fluid Incompatibility

## � Included Tasks Support
| Task # | Description | Supported Features |
|--------|-------------|--------------------|
| 1 | Outlier detection | Explicit abnormal records |
| 2 | Logical inconsistencies | Fluid/formation mismatches |
| 3 | Missing values | 5% salinity data missing |
| 4 | Numerical normalization | float32 scaled values |
| 5 | Text standardization | Categorical normalization |
| 6 | Data processing module | Clean parquet output |
| 7 | AI modeling | Balanced damage types |
| 9 | Model evaluation | Clear normal/abnormal split |

## 🏷️ Column Descriptions
| Column | Type | Range/Values | Description |
|--------|------|--------------|-------------|
| Well_ID | category | WELL_0000000-ABN_0500000 | Well identifier |
| Formation | category | Carbonate, Sandstone, Shale, Dolomite, Mixed | Rock formation type |
| Fluid_Type | category | Brine, Acid, Mud, Water-Based, Oil-Based | Drilling fluid type |
| Temperature_C | float32 | 50-400°C | Bottomhole temperature |
| Pressure_psi | float32 | 1,000-30,000 psi | Downhole pressure |
| Damage_Type | category | 10 damage types | Primary damage classification |

## 💾 Storage Optimization
- Uses parquet format for:
  - Columnar storage
  - Efficient compression
  - Fast read/write operations
- Type optimizations:
  - float32 instead of float64
  - Categorical for text fields

## 🛠️ Suggested Usage
```python
import pandas as pd

# Load dataset
df = pd.read_parquet("formation_damage_optimized.parquet")

# Example: Filter abnormal data
abnormal = df[df["Well_ID"].str.startswith("ABN_")]

```
