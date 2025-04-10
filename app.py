import streamlit as st
st.set_page_config(page_title="Design and Implementation of IoT and ML based Smart Chair for Health Monitoring and Recommendations", layout="wide")

import pandas as pd
import joblib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load model
@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

model = load_model()

# Features used to train the model
model_features = [
    'FSR0', 'FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5',
    'FSR6', 'FSR7', 'FSR8', 'FSR9', 'FSR10', 'FSR11',
    'AccelX', 'AccelY', 'AccelZ',
    'GyroX', 'GyroY', 'GyroZ'
]

# Correction tips dictionary
posture_corrections = {
    'A': "Ideal posture! Keep your back straight, shoulders relaxed, and feet flat on the floor.",
    'B': "Sit back and use the backrest for support.",
    'C': "Distribute your weight evenly on both hips.",
    'D': "Shift your weight evenly between both sides.",
    'E': "Keep your back upright instead of reclining too much.",
    'F': "Uncross your legs and place both feet flat on the floor.",
    'G': "Keep both feet on the ground to maintain spinal balance.",
    'H': "Avoid hunching forward, sit back into the chair.",
    'I': "Move back into the seat fully for lumbar support.",
    'J': "Uncross your legs and keep feet flat on the floor.",
    'K': "Keep both feet grounded for better balance.",
    'L': "Place both feet flat on the ground.",
    'M': "Sit upright with lower back support.",
    'N': "Move back into the chair to use lumbar support.",
    'O': "Keep feet flat on the floor to reduce hip strain.",
    'P': "Ensure both feet are flat on the floor.",
    'Q': "Avoid excessive leaning back and keep your feet grounded.",
    'R': "Uncross your legs and maintain an even weight distribution.",
    'S': "Avoid twisting your torso for long durations.",
    'T': "Keep your back straight and avoid constant twisting."
}

# Quality levels
posture_quality_map = {
    'A': 'Good',
    'C': 'Average', 'D': 'Average', 'E': 'Average', 'F': 'Average', 'G': 'Average',
    'B': 'Bad', 'H': 'Bad', 'I': 'Bad', 'J': 'Bad', 'K': 'Bad', 'L': 'Bad', 'M': 'Bad',
    'N': 'Bad', 'O': 'Bad', 'P': 'Bad', 'Q': 'Bad', 'R': 'Bad', 'S': 'Bad', 'T': 'Bad'
}

# Load Google Sheet data
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqPRHzgtmub8COW-9yQAu2qpYljeGQio6yXs5IKf5hm96dRGXsOipGGrLaH80h7AQVEbzb5lpTK9it/pub?output=csv"
    df = pd.read_csv(url)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df.dropna(subset=['Timestamp'], inplace=True)
    df['DHTHumidity'] = df['DHTHumidity'].replace(-1, pd.NA).ffill()
    return df

df = load_data()

# Sidebar Navigation
page = st.sidebar.selectbox("📄 Choose View", ["Live Analytics", "Detailed Analytics", "About"])

if page != "About":
    selected_date = st.date_input("📅 Select a date", datetime.today().date())
    filtered_df = df[df['Timestamp'].dt.date == selected_date]

# ---------------------------------------
# 🟢 LIVE ANALYTICS
# ---------------------------------------
if page == "Live Analytics":
    st.title("🪑 Live Posture Monitoring & Daily Analysis")

    if not filtered_df.empty:
        # ML prediction
        filtered_df['Predicted_Label'] = model.predict(filtered_df[model_features])
        filtered_df['Posture_Quality'] = filtered_df['Predicted_Label'].map(posture_quality_map)
        filtered_df['Hour'] = filtered_df['Timestamp'].dt.hour

        latest = filtered_df.iloc[-1]
        posture = latest['Predicted_Label']
        correction = posture_corrections.get(posture, "No correction available.")

        # Current Status
        st.subheader("🧍 Current Posture")
        st.success(f"**Posture:** `{posture}`")
        st.info(f"**Correction Tip:** {correction}")
        st.metric("Temperature", f"{latest['MPUTemp']} °C")
        st.metric("Humidity", f"{latest['DHTHumidity']} %")

        # 1. Posture Count
        st.subheader("📊 Posture Frequency")
        fig1 = px.bar(filtered_df['Predicted_Label'].value_counts().reset_index(),
                      x='index', y='Predicted_Label', labels={'index': 'Posture', 'Predicted_Label': 'Count'},
                      title="Posture Count (hover to see exact)", hover_data=["Predicted_Label"])
        st.plotly_chart(fig1, use_container_width=True)

        # 2. Quality Over Time
        st.subheader("📈 Posture Quality Timeline")
        qmap = {'Bad': 0, 'Average': 1, 'Good': 2}
        filtered_df['Quality_Score'] = filtered_df['Posture_Quality'].map(qmap)
        fig2 = px.line(filtered_df, x='Timestamp', y='Quality_Score', title="Posture Quality (Good > Bad)")
        fig2.update_yaxes(tickvals=[0, 1, 2], ticktext=['Bad', 'Average', 'Good'])
        st.plotly_chart(fig2, use_container_width=True)

        # 3. Pie Chart
        st.subheader("🥧 Posture Quality Proportion")
        fig3 = px.pie(filtered_df['Posture_Quality'].value_counts().reset_index(),
                      names='index', values='Posture_Quality', title="Posture Quality Distribution")
        st.plotly_chart(fig3, use_container_width=True)

        # 4. Time Spent per Posture
        st.subheader("⏱️ Time Spent per Posture")
        filtered_df['TimeSpent'] = filtered_df['Timestamp'].diff().dt.total_seconds().fillna(0)
        fig4 = px.bar(filtered_df.groupby('Predicted_Label')['TimeSpent'].sum().reset_index(),
                      x='Predicted_Label', y='TimeSpent', title="Seconds Spent per Posture")
        st.plotly_chart(fig4, use_container_width=True)

        # 5. Heatmap by Hour
        st.subheader("🕒 Posture Frequency by Hour")
        hourly = filtered_df.groupby(['Hour', 'Predicted_Label']).size().reset_index(name='Count')
        fig5 = px.density_heatmap(hourly, x='Hour', y='Predicted_Label', z='Count', title="Heatmap by Hour")
        st.plotly_chart(fig5, use_container_width=True)

        # 6. Transitions
        st.subheader("🔁 Posture Transitions")
        filtered_df['Shifted'] = filtered_df['Predicted_Label'].shift()
        filtered_df['Changed'] = filtered_df['Predicted_Label'] != filtered_df['Shifted']
        transitions = filtered_df['Changed'].sum()
        st.info(f"🌀 You changed posture **{int(transitions)} times** today.")

    else:
        st.warning("No data available for this date.")

# ---------------------------------------
# 🔵 DETAILED ANALYTICS
# ---------------------------------------
elif page == "Detailed Analytics":
    st.title("📊 Environmental Sensor Trends")

    if not filtered_df.empty:
        for col in ['MPUTemp', 'DHTHumidity', 'DHTTemp']:
            if col in filtered_df.columns:
                fig = px.line(filtered_df, x='Timestamp', y=col, title=f"{col} over Time")
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Full Data View"):
            st.dataframe(filtered_df[['Timestamp', 'MPUTemp', 'DHTHumidity', 'DHTTemp']])
    else:
        st.warning("No data for the selected date.")

# ---------------------------------------
# ℹ️ ABOUT PAGE
# ---------------------------------------
elif page == "About":
    st.title("🪑 Smart Chair: IoT & ML-Powered Health Monitoring System")
    st.image("im1.jpg", use_column_width=True)
    st.markdown("""
## **Welcome to the Smart Chair Platform! 🧠💺📊**

Our mission is to revolutionize how we sit by transforming traditional seating into a health-conscious experience. Using advanced **IoT sensors**, **machine learning models**, and **real-time data processing**, the Smart Chair monitors posture, predicts health risks, and provides live ergonomic feedback to improve well-being.

---

### 🔧 **Technologies Used**
- **Internet of Things (IoT)**
- **Machine Learning Models**
- **Streamlit – Frontend Dashboard**
- **Google Sheets – Real-Time Cloud Storage**

---

## ⚙️ **How It Works**

### 1. Data Collection
- 12 FSR sensors (pressure)
- MPU-6050 (tilt + movement)
- DHT22 (temperature + humidity)
- LED indicators for feedback

### 2. Real-Time Analysis
- ML model classifies postures
- Dashboard shows trends and triggers alerts

### 3. Predictive Insights
- Posture prediction and evaluation
- Daily health summaries

### 4. Feedback & Recommendations
- LED alerts + mobile notifications
- Personalized insights on dashboard

---

## 🧩 Components and Flow
""")
    st.image("circuit.jpg", use_column_width=True)
    st.markdown("""
- **ESP32 Microcontroller**
- **12× FSRs + Multiplexer**
- **MPU-6050**
- **DHT22**
- **LED Feedback**
- **Power supply**

---

## 🌟 Why Choose Our Smart Chair?
✅ **Health-Focused**  
✅ **Live Feedback**  
✅ **Non-Invasive**  
✅ **Data-Driven**  
✅ **User-Centric**

---

## 🚀 Get Started
Check the sidebar for:
- **Posture Dashboard**
- **Daily Analytics**
- **Environment Monitoring**

---

## 🙋‍♂️ About Us

[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/Arunoth-SymenA)  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/arunothsymen/)

---

### **Problem Statement**
The modern sedentary lifestyle leads to posture-related health issues. Conventional furniture lacks real-time monitoring or personalized recommendations.

---

### **Proposed Solution**
A smart, sensor-driven, ML-based system integrated into a chair to track posture, analyze health risks, and offer live feedback. Designed to be non-intrusive and connected.

""")
