import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from typing import Dict

class DataCleaner:
    def __init__(self):
        self.imputation_strategies = {
            'median': SimpleImputer(strategy='median'),
            'mean': SimpleImputer(strategy='mean'),
            'knn': KNNImputer(n_neighbors=5),
            'iterative': IterativeImputer(max_iter=10, random_state=42)
        }
        self.imputation_history = []

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = 'median',
        custom_strategy: Dict[str, str] = None
    ) -> pd.DataFrame:
        """
        مدیریت پیشرفته مقادیر گم‌شده با قابلیت‌های:
        - ایمپوت عددی با روش‌های مختلف (`median`, `mean`, `knn`, `iterative`)
        - ایمپوت `NaN` در ستون‌های متنی با رایج‌ترین مقدار (`mode`)
        - ثبت تاریخچه تغییرات برای تحلیل پردازش‌ها
        
        پارامترها:
            df: دیتافریم ورودی
            strategy: استراتژی پیش‌فرض برای ستون‌های عددی
            custom_strategy: دیکشنری مشخص کننده استراتژی برای ستون‌های خاص
            
        مثال:
            cleaner.handle_missing_values(df, strategy='mean',
                                custom_strategy={'Salinity_ppm': 'knn'})
        """
        if df is None or not isinstance(df, pd.DataFrame):
            raise ValueError("❌ خطا: ورودی باید یک DataFrame معتبر باشد!")

        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # ✅ مدیریت ایمپوت سفارشی برای ستون‌های عددی
        if custom_strategy:
            for col, col_strategy in custom_strategy.items():
                if col in numeric_cols:
                    imputer = self.imputation_strategies.get(col_strategy)
                    if imputer:
                        df[[col]] = imputer.fit_transform(df[[col]])
                        self.imputation_history.append(
                            f"Column '{col}' imputed with {col_strategy}"
                        )
                        numeric_cols.remove(col)
                    else:
                        raise ValueError(f"❌ خطا: استراتژی ایمپوت '{col_strategy}' معتبر نیست!")

        # ✅ مدیریت ایمپوت عمومی برای ستون‌های عددی باقی‌مانده
        if numeric_cols:
            imputer = self.imputation_strategies.get(strategy)
            if imputer:
                df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
                self.imputation_history.append(
                    f"Columns {numeric_cols} imputed with {strategy}"
                )
            else:
                raise ValueError(f"❌ خطا: استراتژی ایمپوت '{strategy}' معتبر نیست!")

        # ✅ ایمپوت `NaN` در ستون‌های متنی با رایج‌ترین مقدار (`mode`)
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            if df[col].isna().sum() > 0:  # فقط اگر مقدار `NaN` دارد
                df[col].fillna(df[col].mode()[0], inplace=True)
                self.imputation_history.append(f"Categorical column '{col}' imputed with mode")
            
        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """حذف سطرهای تکراری با حفظ اولین occurrence"""
        if df is None or not isinstance(df, pd.DataFrame):
            raise ValueError("❌ خطا: ورودی باید یک DataFrame معتبر باشد!")

        initial_count = len(df)
        df = df.drop_duplicates()
        removed = initial_count - len(df)
        self.imputation_history.append(
            f"Removed {removed} duplicate rows"
        )
        return df
