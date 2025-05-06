# مستندسازی کد پردازش و مدیریت Outlierها در داده‌های آسیب سازند

این کد برای شناسایی و مدیریت داده‌های پرت (Outlier) در یک دیتاست مربوط به آسیب سازند طراحی شده است. با استفاده از روش IQR (فاصله بین چارکی)، outlierها تشخیص داده شده و با دو روش «حذف» یا «جایگزینی با مقادیر حدی» پردازش می‌شوند.

## فهرست مطالب
1. [پیکربندی]
2. [تشخیص Outlierها]
   - [تابع detect_outliers_iqr]
   - [تابع generate_outliers_report]
3. [پردازش داده‌ها]
   - [تابع handle_outliers]
4. [اجرای اصلی]
5. [نمونه خروجی]

---
1. [پیکربندی]
## پیکربندی <a name="پیکربندی"></a>
- **مسیر فایل‌ها:**
  - `INPUT_FILE`: مسیر فایل ورودی (فرمت Parquet)
  - `OUTLIERS_REPORT_FILE`: مسیر ذخیره گزارش outlierها
  - `CLEANED_DATA_FILE`: مسیر ذخیره داده‌های پردازش شده
- **ستون‌های مورد بررسی:**  
  ستون‌های عددی شامل دما، فشار، نفوذپذیری و نرخ جریان
- **روش پردازش:**  
  `ACTION` می‌تواند `clip` (جایگزینی با مقادیر حدی) یا `remove` (حذف رکوردها) باشد.
- **آستانه تشخیص Outlier:**  
  مقدار پیش‌فرض `IQR_THRESHOLD = 1.5` (مطابق استاندارد)

2. [تشخیص Outlierها]
تشخیص Outlierها <a name="تشخیص-outlierها"></a>
تابع detect_outliers_iqr <a name="تابع-detect_outliers_iqr"></a>
هدف: تشخیص outlierها در یک ستون با روش IQR

ورودی‌ها:

data: DataFrame حاوی داده‌ها

column: نام ستون مورد بررسی

threshold: آستانه IQR (پیش‌فرض: 1.5)

خروجی:

DataFrame شامل outlierها و اطلاعات حد بالا/پایین

Tuple (lower_bound, upper_bound) حدود محاسبه شده

مراحل محاسبه:

محاسبه چارک اول (Q1) و چارک سوم (Q3)

محاسبه IQR = Q3 - Q1

تعیین حدود:

حد پایین: Q1 - (threshold * IQR)

حد بالا: Q3 + (threshold * IQR)

علامت‌گذاری outlierها و افزودن ستون‌های Bound_Type و Bound_Value

تابع generate_outliers_report <a name="تابع-generate_outliers_report"></a>
هدف: تولید گزارش جامع از outlierها برای تمام ستون‌های مشخص شده

ورودی‌ها:

df: DataFrame اصلی

columns: لیست ستون‌های مورد بررسی

خروجی:

DataFrame تجمیعی از تمام outlierها

دیکشنری bounds_info شامل حدود هر ستون

نکات:

گزارش به صورت فایل Parquet ذخیره می‌شود.

در صورت عدم وجود outlier، فایلی ایجاد نمی‌شود.

3. [پردازش داده‌ها]
پردازش داده‌ها <a name="پردازش-دادهها"></a>
تابع handle_outliers <a name="تابع-handle_outliers"></a>
هدف: مدیریت outlierها با روش انتخابی (clip یا remove)

ورودی‌ها:

df: DataFrame اصلی

bounds_info: دیکشنری حدود هر ستون

action: روش پردازش (پیش‌فرض: ACTION از تنظیمات)

خروجی:
DataFrame پردازش شده و ذخیره آن در فایل Parquet

روش‌های پردازش:

clip: جایگزینی مقادیر خارج از حد با مقادیر حدی

remove: حذف رکوردهای خارج از محدوده

بهینه‌سازی ذخیره‌سازی:
تبدیل ستون‌های مشخص شده به نوع category برای کاهش حجم ذخیره‌سازی.

4. [اجرای اصلی]
اجرای اصلی <a name="اجرای-اصلی"></a>
بررسی وجود فایل ورودی

بارگذاری داده‌ها و نمایش تعداد رکوردها

تولید گزارش outlierها

پردازش داده‌ها و نمایش نمونه تغییرات

چاپ خلاصه آماری

5. [نمونه خروجی]
نمونه خروجی <a name="نمونه-خروجی"></a>

[STATUS] Dataset loaded with 10,500,000 records
[SUCCESS] Outlier report saved to 'outliers_report.parquet'
[SUCCESS] Cleaned dataset saved to 'formation_damage_cleaned.parquet'

[SAMPLE CHANGES] Example modifications:
Pressure_psi (Well ABN_0374655):
  Original: 25115.66 → Cleaned: 23045.47
  Upper bound: 23045.47

Permeability_mD (Well ABN_0451911):
  Original: 1190.88 → Cleaned: 787.72
  Upper bound: 787.72

Temperature_C (Well ABN_0188547):
  Original: 304.71 → Cleaned: 286.24
  Upper bound: 286.24


[SUMMARY] Initial records: 10,500,000
          Outliers detected: 1,497,486
          Final records: 10,500,000