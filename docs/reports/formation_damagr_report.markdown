```
# Formation Damage Prediction Pipeline

این پروژه یک سیستم خودکار برای بازآموزی مدل یادگیری ماشین جهت پیش‌بینی نوع آسیب سازند (`Damage_Type`) در چاه‌های نفت و گاز پیاده‌سازی می‌کند. سیستم از داده‌های عملیاتی جدید (از Kafka)، زمان‌بندی بازآموزی هر 7 روز (با Airflow)، و ردیابی عملکرد مدل (با MLflow) استفاده می‌کند.

## ویژگی‌ها
- خواندن داده از فایل parquet یا Kafka.
- پیش‌پردازش داده با مدیریت ستون‌های کیفی توسط LightGBM.
- آموزش مدل `LGBMClassifier` با ردیابی در MLflow.
- زمان‌بندی بازآموزی با Airflow.
- ذخیره مدل و LabelEncoder در Google Drive.

## پیش‌نیازها
- Python 3.8 یا بالاتر
- سرور Kafka (لوکال یا ابری مانند Confluent Cloud)
- سرور MLflow (برای ردیابی مدل)
- سرور Airflow (برای زمان‌بندی)
- حساب ngrok (برای دسترسی به MLflow در Colab)
- کتابخانه‌های مورد نیاز:
  ```bash
  pip install -r requirements.txt
```

## ساختار پروژه

```
formation-damage-pipeline/
├── formation_damage_pipeline.py  # کد اصلی (پیش‌پردازش، آموزش، و اجرای اولیه)
├── formation_damage_dag.py       # تعریف DAG برای Airflow
├── requirements.txt              # لیست وابستگی‌ها
├── README.md                    # مستندات پروژه
```

## ساختار داده

دیتاست شامل 10.5 میلیون ردیف و 8 ستون است:

- **ویژگی‌ها**:
  - `Formation`, `Fluid_Type`, `Completion_Type` (کیفی)
  - `Temperature_C`, `Pressure_psi`, `Permeability_mD`, `Porosity_pct` (کمی)
- **هدف**: `Damage_Type` (کتگوریکال، شامل 10 کلاس مانند `Filtration Problem`, `Corrosion Cracking`)

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. تنظیم Kafka

- **لوکال**: Kafka و Zookeeper را نصب و روی `localhost:9092` اجرا کنید. تاپیک `formation_damage_topic` را ایجاد کنید:

  ```bash
  bin/kafka-topics.sh --create --topic formation_damage_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
  ```
- **ابری**: از Confluent Cloud استفاده کنید و `bootstrap.servers`, `sasl.username`, `sasl.password` را در `fetch_kafka_data` تنظیم کنید.

### 3. تنظیم MLflow

- سرور MLflow را اجرا کنید:

  ```bash
  mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db
  ```
- در Colab، authtoken ngrok را از dashboard.ngrok.com دریافت و در کد وارد کنید.

### 4. تنظیم Airflow

- Airflow را نصب کنید:

  ```bash
  pip install apache-airflow
  airflow db init
  ```
- فایل `formation_damage_dag.py` را در پوشه `~/airflow/dags/` کپی کنید.
- وب‌سرور و زمان‌بندی‌کننده Airflow را اجرا کنید:

  ```bash
  airflow webserver --port 8080 &
  airflow scheduler &
  ```

## اجرای پروژه

### در Google Colab

1. فایل `formation_damage_pipeline.py` را آپلود کنید.
2. فایل `formation_damage_optimized.parquet` را در `/content/drive/MyDrive/` قرار دهید.
3. authtoken ngrok را وارد کنید:

   ```python
   ngrok_authtoken = "YOUR_AUTHTOKEN_HERE"
   ```
4. کد را اجرا کنید:

   ```bash
   python formation_damage_pipeline.py
   ```

### در سیستم لوکال

1. Kafka، MLflow، و Airflow را راه‌اندازی کنید.
2. فایل `formation_damage_pipeline.py` را برای تست اولیه اجرا کنید:

   ```bash
   python formation_damage_pipeline.py
   ```
3. برای بازآموزی خودکار، DAG را در Airflow فعال کنید.

## نتایج

- **دقت فعلی**: آموزش: 43.74%، آزمون: 12.39% (به دلیل عدم تعادل کلاس‌ها یا ویژگی‌های ناکافی).
- **بهبود پیشنهادی**:
  - استفاده از `class_weight='balanced'` در `LGBMClassifier`.
  - جستجوی گرید برای بهینه‌سازی هایپرپارامترها.
  - مهندسی ویژگی یا افزایش نمونه‌ها.

## محدودیت‌ها

- **Colab**: Airflow قابل اجرا نیست؛ از سرور Airflow استفاده کنید.
- **Kafka**: نیاز به سرور فعال (لوکال یا ابری).
- **دقت پایین**: نیاز به بررسی داده‌ها برای همبستگی غیرمنطقی یا مهندسی ویژگی.

## مشارکت

برای گزارش باگ یا پیشنهاد بهبود، لطفاً یک Issue در GitHub ایجاد کنید یا Pull Request ارسال کنید.

---

آخرین به‌روزرسانی: 22 می 2025

```
```