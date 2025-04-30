import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier


# read dataset
data = pd.read_csv('formation_damage_dataset_cleaned.csv')

# features & Label
X = data[['Fluid_Type', 'Completion_Type', 'Formation', 
            'Temperature_C', 'Pressure_psi', 'pH', 'Salinity_ppm', 
            'Flow_Rate_bbl_day', 'Permeability_mD', 'Porosity_pct']]
y = data['Damage_Type']

# train & test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

#features preprocessor (1-sacling numeric data  2-OneHotEncoding string data)
preprocessor = make_column_transformer(
    (StandardScaler(), ['Temperature_C', 'Pressure_psi', 'pH', 
                        'Salinity_ppm', 'Flow_Rate_bbl_day', 
                        'Permeability_mD', 'Porosity_pct']),
    (OneHotEncoder(handle_unknown='ignore'), ['Fluid_Type', 'Completion_Type', 'Formation'])
)

#pipeline (1-preprocssing   2-model)
model = make_pipeline(
    preprocessor,
    RandomForestClassifier(random_state=42)
)

#model learning
model.fit(X_train, y_train)
ypred=model.predict(y_train)
print("✅Learn Random-Forest model")
