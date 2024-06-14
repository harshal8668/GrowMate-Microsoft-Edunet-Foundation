import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pickle

# # Load data
# file = pd.read_csv("Dataset/Crop_recommendation_new1.csv")

# file = file.rename(columns={'label': 'crop'})
# file.dropna(subset=['N'], inplace=True)

# crop_dict = {
#     'rice': 1,
#     'maize': 2,
#     'jute': 3,
#     'cotton': 4,
#     'coconut': 5,
#     'papaya': 6,
#     'orange': 7,
#     'apple': 8,
#     'muskmelon': 9,
#     'watermelon': 10,
#     'grapes': 11,
#     'mango': 12,
#     'banana': 13,
#     'pomegranate': 14,
#     'lentil': 15,
#     'blackgram': 16,
#     'mungbean': 17,
#     'mothbeans': 18,
#     'pigeonpeas': 19,
#     'kidneybeans': 20,
#     'chickpea': 21,
#     'coffee': 22
# }
# file['crop_num'] = file['crop'].map(crop_dict)
# file['land_type_num'] = file['land_type'].map({"Hilly": 0, "plain": 1})

# x = file.drop(columns=['crop', 'crop_num', 'land_type', 'land_type_num'], axis=1)
# y = file['crop_num']

# # Split data
# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=69)

# # Scale data
# ms = MinMaxScaler()
# x_train = ms.fit_transform(x_train)
# x_test = ms.transform(x_test)

# sc = StandardScaler()
# sc.fit(x_train)
# x_train = sc.transform(x_train)
# x_test = sc.transform(x_test)

# # Train RandomForestClassifier
# rfc = RandomForestClassifier()
# rfc.fit(x_train, y_train)

# # Save models
# pickle.dump(rfc, open('model.pkl', 'wb'))
# pickle.dump(ms, open('minmaxscaler.pkl', 'wb'))
# pickle.dump(sc, open('standscaler.pkl', 'wb'))

# Load models
rfc = pickle.load(open('model.pkl', 'rb'))
ms = pickle.load(open('minmaxscaler.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))

def recommendation(N, P, k, temperature, humidity, ph, rainfall):
    features = np.array([[N, P, k, temperature, humidity, ph, rainfall]])
    transformed_features = ms.transform(features)
    transformed_features = sc.transform(transformed_features)
    prediction = rfc.predict(transformed_features)
    return prediction[0]

crop_dict_reverse = {v: k for k, v in crop_dict.items()}

# Streamlit App
st.title('Crop Recommendation System')

N = st.number_input('Nitrogen (N)', min_value=0, max_value=100, value=50)
P = st.number_input('Phosphorus (P)', min_value=0, max_value=100, value=50)
k = st.number_input('Potassium (K)', min_value=0, max_value=100, value=50)
temperature = st.number_input('Temperature (°C)', min_value=-10.0, max_value=60.0, value=25.0)
humidity = st.number_input('Humidity (%)', min_value=0, max_value=100, value=50)
ph = st.number_input('pH', min_value=0.0, max_value=14.0, value=7.0)
rainfall = st.number_input('Rainfall (mm)', min_value=0, max_value=500, value=100)

if st.button('Recommend Crop'):
    prediction = recommendation(N, P, k, temperature, humidity, ph, rainfall)
    crop_name = crop_dict_reverse.get(prediction, "Unknown crop")
    st.write(f"The recommended crop for the given conditions is: {crop_name}")

