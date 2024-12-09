# -*- coding: utf-8 -*-
"""Air Quality and Pollution Assessment Classification

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fu3dG-0XUnzRWEOMUfSSvvVOhirRZ3D8
"""

import pandas as pd
import numpy as np
import  matplotlib.pyplot as plt
import seaborn as sns

# model
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

"""## **Data Loading**"""

import kagglehub

# Download latest version
path = kagglehub.dataset_download("mujtabamatin/air-quality-and-pollution-assessment")

print("Path to dataset files:", path)

air_df = pd.read_csv(path + "/updated_pollution_dataset.csv")
air_df.head()

"""**Key Features:**

  * Temperature (°C): Average temperature of the region.
  * Humidity (%): Relative humidity recorded in the region.
  * PM2.5 Concentration (µg/m³): Fine particulate matter levels.
  * PM10 Concentration (µg/m³): Coarse particulate matter levels.
  * NO2 Concentration (ppb): Nitrogen dioxide levels.
  * SO2 Concentration (ppb): Sulfur dioxide levels.
  * CO Concentration (ppm): Carbon monoxide levels.
  * Proximity to Industrial Areas (km): Distance to the nearest industrial zone.
  * Population Density (people/km²): Number of people per square kilometer in the region.

**Target Variable: Air Quality Levels**

  * Good: Clean air with low pollution levels.
  * Moderate: Acceptable air quality but with some pollutants present.
  * Poor: Noticeable pollution that may cause health issues for sensitive groups.
  * Hazardous: Highly polluted air posing serious health risks to the population.

### **Encode Target**
"""

air_df['Air Quality'].unique()

label_encoder = LabelEncoder()
air_df['Air Quality'] = label_encoder.fit_transform(air_df['Air Quality'])

air_df.head()
print(air_df['Air Quality'].unique())
print(label_encoder.classes_)

"""## **EDA**"""

air_df.info()

air_df.describe()

print(f"Jumlah data: {air_df.shape[0]}")
print(f"Jumlah data kosong : {air_df.isna().sum().to_dict()}")
print(f"Jumlah data duplicated : {air_df.duplicated().sum()}")

"""### **Handling Outliers**"""

import math

numerical_features = air_df.select_dtypes(include=['int64', 'float64']).columns.to_list()

# Tentukan jumlah kolom dan baris
n_cols = 3  # Jumlah kolom dalam grid
n_rows = math.ceil(len(numerical_features) / n_cols)  # Hitung jumlah baris berdasarkan jumlah fitur

# Buat grid plot
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 5))

# Flatten axes agar iterasi lebih mudah
axes = axes.flatten()

# Iterasi setiap fitur numerik dan buat boxplot
for i, feature in enumerate(numerical_features):
    sns.boxplot(y=air_df[feature], ax=axes[i], color='skyblue')
    axes[i].set_title(f"Boxplot for {feature}")

# Hapus subplot kosong jika jumlah fitur tidak genap
for j in range(len(numerical_features), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

numeric_columns = air_df.select_dtypes(include=['number'])

# Hitung Q1, Q3, dan IQR
Q1 = numeric_columns.quantile(0.25)
Q3 = numeric_columns.quantile(0.75)
IQR = Q3 - Q1

# Drop outliers
air_df = air_df[~((numeric_columns < (Q1 - 1.5 * IQR)) | (numeric_columns > (Q3 + 1.5 * IQR))).any(axis=1)]

# Cek ukuran dataset setelah kita drop outliers
air_df.shape

"""### **Univariate Analysis**"""

features = numerical_features[:-1]

plt.figure(figsize=(8, 25))
for i, feature in enumerate(features):
    plt.subplot(len(features), 1, i + 1)
    sns.histplot(air_df[feature], kde=True, color='blue')
    plt.title(f"Histogram of {feature}")
    plt.tight_layout()
plt.show()

"""### **Multivariate Analysis**"""

plt.figure(figsize=(10, 8))
correlation_matrix = air_df[numerical_features].corr().round(2)

# Untuk menge-print nilai di dalam kotak, gunakan parameter anot=True
sns.heatmap(data=correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, )
plt.title("Correlation Matrix untuk Fitur Numerik ", size=20)

# Membuang 2 feature yang memilki korelasi terendah dengan Target
air_df.drop(columns=['Proximity_to_Industrial_Areas', 'PM2.5'], inplace=True, axis=1)
air_df.head()

"""## **Data Preparation**

### **Train-Test-Split**
"""

X = air_df.drop(columns=['Air Quality'])
y = air_df['Air Quality']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.2, random_state=42)

print(f"Data train: {X_train.shape[0]}")
print(f"Data test: {X_test.shape[0]}")

"""### **Standarisasi**"""

numerical_features = air_df.select_dtypes(include=['int64', 'float64']).columns.to_list()
numerical_features.remove('Air Quality')
numerical_features

scaller = StandardScaler()
X_train = scaller.fit_transform(X_train)
X_test = scaller.transform(X_test)

air_df[numerical_features] = scaller.fit_transform(air_df[numerical_features])
air_df.head()

"""## **Model**"""

# Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# KNN
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train, y_train)

# XGB
xgb_model = XGBClassifier(random_state=42)
xgb_model.fit(X_train, y_train)

"""## **Evaluasi Model**"""

# Prediksi menggunakan model pertama Random Forest
y_pred_rf = rf_model.predict(X_test)

# Prediksi menggunakan model kedua (KNN)
y_pred_knn = knn_model.predict(X_test)

# Prediksi menggunakan model adaboost
y_pred_xgb = xgb_model.predict(X_test)

# Rekap evaluasi kedua model
print("Model Evaluation Summary:\n")

print("Random Forest Model")
print("Accuracy: {:.2f}".format(accuracy_score(y_test, y_pred_rf)))
print("Classification Report:\n", classification_report(y_test, y_pred_rf))

print("KNN Model")
print("Accuracy: {:.2f}".format(accuracy_score(y_test, y_pred_knn)))
print("Classification Report:\n", classification_report(y_test, y_pred_knn))

print("XGB Model")
print("Accuracy: {:.2f}".format(accuracy_score(y_test, y_pred_xgb)))
print("Classification Report:\n", classification_report(y_test, y_pred_xgb))

"""Dari hasil di atas Algoritma The Forest merpukana algoritma terbaik dalam kasus klasifikasi ini dengan accuracy mencapai 95%"""

# save model Random Forest
import pickle
pickle.dump(rf_model, open('model.pkl', 'wb'))
pickle.dump(scaller, open('scaller.pkl', 'wb'))

"""### **UJI DATA**"""

import pandas
import pickle

# load model dan scaller
model = pickle.load(open('model.pkl', 'rb'))
scaller = pickle.load(open('scaller.pkl', 'rb'))

# 'Good' - 'Hazardous' - 'Moderate' - 'Poor'
air_quality = ['Baik', 'Berbahaya', 'Sedang', 'Buruk']

# contoh data test
data_test = pandas.DataFrame({
    'Temperature': [29.8],
    'Humidity': [59.1],
    'PM10': [17.9],
    'NO2': [18.9],
    'SO2': [9.2],
    'CO': [1.72],
    'Population_Density': [319]
})

data_test = scaller.transform(data_test)
prediction = model.predict(data_test)

print(f"Tingkat kualitas udara tempat anda berada pada tingkat {air_quality[prediction[0]]}")

"""**Keterangan**:
  * Temperature (°C): Suhu rata-rata wilayah tersebut.
  * Humidity (%): Kelembaban relatif yang tercatat di wilayah tersebut.
  * PM10 Concentration (µg/m³): Tingkat materi partikulat kasar.
  * NO2 Concentration (ppb): Tingkat nitrogen dioksida.
  * SO2 Concentration (ppb): Tingkat sulfur dioksida.
  * CO Concentration (ppm): Tingkat karbon monoksida.
  * Population Density (people/km²): Jumlah orang per kilometer persegi di wilayah tersebut.
"""

try :
  Temperature	= float(input("Masukan Temperature: "))
  Humidity = float(input("Masukan Humidity: "))
  PM10 = float(input("Masukan PM10: "))
  NO2 = float(input("Masukan NO2: "))
  SO2 = float(input("Masukan SO2: "))
  CO = float(input("Masukan CO: "))
  Population_Density = int(input("Masukan Population_Density: "))
except ValueError:
  print("Input Ga sesuai. Masukan Input Yang bener.")

new_data = pandas.DataFrame({
  'Temperature': [29.8],
  'Humidity': [59.1],
  'PM10': [17.9],
  'NO2': [18.9],
  'SO2': [9.2],
  'CO': [1.72],
  'Population_Density': [319]
})

new_data = scaller.transform(new_data)
prediction = model.predict(new_data)

print(f"Tingkat kualitas udara tempat anda berada pada tingkat {air_quality[prediction[0]]}")