import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self):
        self.feature_list = []

    def add_pt_ratio(self, df):
        """نسبت فشار به دما (Pressure/Temperature Ratio)"""
        df['PT_Ratio'] = df['Pressure_psi'] / (df['Temperature_C'] + 1e-6)  # جلوگیری از تقسیم بر صفر
        self.feature_list.append('PT_Ratio')
        return df

    def add_flow_efficiency(self, df):
        """بازدهی جریان (Flow Efficiency Metric)"""
        df['Flow_Efficiency'] = (df['Flow_Rate_bbl_day'] * 100) / \
                              (df['Permeability_mD'] * df['Porosity_pct'] + 1e-6)
        self.feature_list.append('Flow_Efficiency')
        return df

    def add_formation_metrics(self, df):
        """ویژگی‌های مرتبط با سازند زمین‌شناسی"""
        df['Carbonate_Flag'] = df['Formation'].apply(lambda x: 1 if x == 'Carbonate' else 0)
        df['Sandstone_Flag'] = df['Formation'].apply(lambda x: 1 if x == 'Sandstone' else 0)
        self.feature_list.extend(['Carbonate_Flag', 'Sandstone_Flag'])
        return df