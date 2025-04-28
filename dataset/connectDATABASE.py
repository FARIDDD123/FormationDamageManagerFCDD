import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('formation_damage_dataset_cleaned.csv')


# DATABASE information 
db_user = 'postgres'
db_password = '22121384'
db_host = 'localhost'
db_port = '5432'
db_name = 'dataset'

#make URL
connection_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

#create engine for connection
engine= create_engine(connection_url)

df.to_sql('formation_damage',engine,index=False,if_exists='replace')
print("✅ Data loaded into PostgreSQL database.")
