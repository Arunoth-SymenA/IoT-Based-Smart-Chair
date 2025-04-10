import streamlit as st
from datetime import datetime
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import win10toast
from win10toast import ToastNotifier  # Notification library for Windows

# Set page configuration
st.set_page_config(
    page_title="Design and Implementation of IoT and ML based Smart Chair for Health Monitoring and Recommendations",
    layout="wide"
)

# Initialize Windows toast notifier for notifications
toaster = ToastNotifier()

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

# Posture correction tips
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

# Full posture names
posture_names = {
    'A': "Upright sitting with backrest",
    'B': "Leaning forward without backrest",
    'C': "Leaning Left",
    'D': "Leaning Right",
    'E': "Lean back",
    'F': "Right Leg Crossed (RLC) and upright",
    'G': "Left Leg Crossed (LLC) and upright",
    'H': "Leaning forward with backrest",
    'I': "Sitting on the front edge",
    'J': "Cross-legged",
    'K': "Left Ankle Resting (LAR) on the right leg",
    'L': "Right Ankle Resting (RAR) on the Left Leg",
    'M': "Lounge",
    'N': "Lean back and sit on the edge",
    'O': "LAR and leaning back",
    'P': "RAR and leaning back",
    'Q': "RLC and leaning back",
    'R': "LLC and leaning back",
    'S': "Rotating the trunk (Left)",
    'T': "Rotating the trunk (Right)"
}

# Posture quality levels
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

# ---------------------------------------
# 📌 Problem Statement & Solution in Sidebar
# ---------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 **Problem Statement**")
st.sidebar.markdown("""The modern lifestyle's shift towards prolonged sedentary activities has led to a surge in health issues such as poor posture, musculoskeletal disorders, obesity, cardiovascular diseases, and mental health concerns. Conventional chairs and workspaces offer no active monitoring or corrective feedback, making users unaware of the harmful effects of improper sitting posture over extended periods.""")

st.sidebar.markdown("### 💡 **Proposed Solution**")
st.sidebar.markdown("""To address these challenges, we propose the development of an **IoT-based Smart Chair system integrated with Machine Learning**. This chair will continuously monitor posture, detect anomalies, predict health risks, and offer real-time feedback via LED and mobile notifications — promoting healthier sitting habits and well-being.""")

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
        filtered_df['Posture_Name'] = filtered_df['Predicted_Label'].map(posture_names)
        filtered_df['Hour'] = filtered_df['Timestamp'].dt.hour

        latest = filtered_df.iloc[-1]
        posture = latest['Predicted_Label']
        correction = posture_corrections.get(posture, "No correction available.")
        full_posture_name = posture_names.get(posture, posture)

        # Current Status
        st.subheader("🧍 Current Posture")
        st.success(f"**Posture:** `{posture}` – {full_posture_name}")
        st.info(f"**Correction Tip:** {correction}")
        st.metric("Temperature", f"{latest['MPUTemp']} °C")
        st.metric("Humidity", f"{latest['DHTHumidity']} %")

        # Send notification if posture quality is bad
        if posture_quality_map[posture] == "Bad":
            toaster.show_toast("Bad Posture Detected!", "Please adjust your posture to avoid health risks.", duration=10)

        # 1. Posture Count
        st.subheader("📊 Posture Frequency")
        posture_counts = filtered_df['Posture_Name'].value_counts().reset_index()
        posture_counts.columns = ['Posture', 'Count']
        fig1 = px.bar(posture_counts, x='Posture', y='Count', title="Posture Count (hover to see exact)", hover_data=["Count"])
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
        quality_counts = filtered_df['Posture_Quality'].value_counts().reset_index()
        quality_counts.columns = ['Quality', 'Count']
        fig3 = px.pie(quality_counts, names='Quality', values='Count', title="Posture Quality Distribution")
        st.plotly_chart(fig3, use_container_width=True)

        # 4. Time Spent per Posture
        st.subheader("⏱️ Time Spent per Posture")
        filtered_df['TimeSpent'] = filtered_df['Timestamp'].diff().dt.total_seconds().fillna(0)
        time_data = filtered_df.groupby('Posture_Name')['TimeSpent'].sum().reset_index()
        fig4 = px.bar(time_data, x='Posture_Name', y='TimeSpent', title="Seconds Spent per Posture")
        st.plotly_chart(fig4, use_container_width=True)

        # 5. Heatmap by Hour
        st.subheader("🕒 Posture Frequency by Hour")
        hourly = filtered_df.groupby(['Hour', 'Posture_Name']).size().reset_index(name='Count')
        fig5 = px.density_heatmap(hourly, x='Hour', y='Posture_Name', z='Count', title="Heatmap by Hour")
        st.plotly_chart(fig5, use_container_width=True)

        # 6. Transitions
        st.subheader("🔁 Posture Transitions")
        filtered_df['Shifted'] = filtered_df['Posture_Name'].shift()
        filtered_df['Changed'] = filtered_df['Posture_Name'] != filtered_df['Shifted']
        transitions = filtered_df['Changed'].sum()
        st.info(f"🌀 You changed posture **{int(transitions)} times** today.")

        # 📥 Download button
        st.subheader("📥 Download Daily Report")
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"posture_data_{selected_date}.csv",
            mime="text/csv"
        )

# ---------------------------------------
# ℹ️ ABOUT PAGE
# ---------------------------------------
elif page == "About":
    st.title("🪑 Smart Chair: IoT & ML-Powered Health Monitoring System")
    st.image("https://cdn.pixabay.com/photo/2020/08/18/09/00/smart-technology-5496932_1280.jpg", use_column_width=True)
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
    st.image("https://cdn.pixabay.com/photo/2016/05/05/02/37/tech-1370954_1280.jpg", use_column_width=True)
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

[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://www.linkedin.com/in/arunothsymen/)  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/arunothsymen/)
""")
