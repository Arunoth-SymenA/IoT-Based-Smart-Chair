import streamlit as st
st.set_page_config(page_title="Smart Chair Dashboard", layout="wide")

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

# Model features
model_features = [
    'FSR0', 'FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5',
    'FSR6', 'FSR7', 'FSR8', 'FSR9', 'FSR10', 'FSR11',
    'AccelX', 'AccelY', 'AccelZ', 'GyroX', 'GyroY', 'GyroZ'
]

# Correction tips
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

# Posture quality classification
posture_quality_map = {
    'A': 'Good',
    'C': 'Average', 'D': 'Average', 'E': 'Average', 'F': 'Average', 'G': 'Average',
    'B': 'Bad', 'H': 'Bad', 'I': 'Bad', 'J': 'Bad', 'K': 'Bad', 'L': 'Bad', 'M': 'Bad',
    'N': 'Bad', 'O': 'Bad', 'P': 'Bad', 'Q': 'Bad', 'R': 'Bad', 'S': 'Bad', 'T': 'Bad'
}

# Load sheet data
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqPRHzgtmub8COW-9yQAu2qpYljeGQio6yXs5IKf5hm96dRGXsOipGGrLaH80h7AQVEbzb5lpTK9it/pub?output=csv"
    df = pd.read_csv(url)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df.dropna(subset=['Timestamp'], inplace=True)
    df['DHTHumidity'] = df['DHTHumidity'].replace(-1, pd.NA).ffill()
    return df

df = load_data()
page = st.sidebar.selectbox("📄 Choose View", ["Live Analytics", "Detailed Analytics"])
selected_date = st.date_input("📅 Select a date", datetime.today().date())
filtered_df = df[df['Timestamp'].dt.date == selected_date]

# ========================
# LIVE ANALYTICS
# ========================
if page == "Live Analytics":
    st.title("🪑 Smart Chair Posture - Daily Posture Analytics")

    if not filtered_df.empty:
        latest = filtered_df.iloc[-1]

        # Predict all postures
        X = filtered_df[model_features]
        predicted_labels = model.predict(X)
        filtered_df['Predicted_Label'] = predicted_labels
        filtered_df['Posture_Quality'] = filtered_df['Predicted_Label'].map(posture_quality_map)
        filtered_df['Hour'] = filtered_df['Timestamp'].dt.hour

        latest_posture = predicted_labels[-1]
        latest_correction = posture_corrections.get(latest_posture, "No correction available.")

        st.subheader("🧍 Current Posture")
        st.success(f"**Posture:** `{latest_posture}`")
        st.info(f"**Correction Tip:** {latest_correction}")

        st.metric("Temperature", f"{latest['MPUTemp']} °C")
        st.metric("Humidity", f"{latest['DHTHumidity']} %")

        # 1. 📊 Posture count
        st.subheader("📊 Posture Frequency")
        posture_counts = filtered_df['Predicted_Label'].value_counts().reset_index()
        posture_counts.columns = ['Posture', 'Count']
        fig1 = px.bar(posture_counts, x='Posture', y='Count', title="Posture Count", hover_data=['Count'])
        st.plotly_chart(fig1, use_container_width=True)

        # 2. 📈 Quality over time
        st.subheader("📈 Posture Quality Timeline")
        quality_numeric = {'Good': 2, 'Average': 1, 'Bad': 0}
        filtered_df['Quality_Score'] = filtered_df['Posture_Quality'].map(quality_numeric)
        fig2 = px.line(filtered_df, x='Timestamp', y='Quality_Score',
                       title="Posture Quality (Good - Avg - Bad)", markers=True)
        fig2.update_yaxes(tickvals=[0, 1, 2], ticktext=['Bad', 'Average', 'Good'])
        st.plotly_chart(fig2, use_container_width=True)

        # 3. 🥧 Quality pie chart
        st.subheader("🥧 Posture Quality Breakdown")
        quality_counts = filtered_df['Posture_Quality'].value_counts().reset_index()
        quality_counts.columns = ['Quality', 'Count']
        fig3 = px.pie(quality_counts, names='Quality', values='Count', title="Posture Quality Pie Chart")
        st.plotly_chart(fig3, use_container_width=True)

        # 4. ⏱️ Time spent in each posture
        st.subheader("⏱️ Time Spent per Posture")
        filtered_df['TimeSpent'] = filtered_df['Timestamp'].diff().dt.total_seconds().fillna(0)
        time_spent = filtered_df.groupby('Predicted_Label')['TimeSpent'].sum().reset_index()
        fig4 = px.bar(time_spent, x='Predicted_Label', y='TimeSpent',
                      title="Time Spent in Each Posture (seconds)", hover_data=['TimeSpent'])
        st.plotly_chart(fig4, use_container_width=True)

        # 5. 📈 Posture frequency by hour
        st.subheader("🕒 Posture Trends by Hour")
        hourly = filtered_df.groupby(['Hour', 'Predicted_Label']).size().reset_index(name='Count')
        fig5 = px.density_heatmap(hourly, x='Hour', y='Predicted_Label', z='Count', color_continuous_scale="Viridis",
                                  title="Posture Frequency by Hour")
        st.plotly_chart(fig5, use_container_width=True)

        # 6. 🔁 Posture transitions
        st.subheader("🔁 Posture Changes Throughout the Day")
        filtered_df['Shifted'] = filtered_df['Predicted_Label'].shift()
        filtered_df['Changed'] = filtered_df['Predicted_Label'] != filtered_df['Shifted']
        transition_count = filtered_df['Changed'].sum()
        st.info(f"🌀 You changed posture **{int(transition_count)} times** today.")

    else:
        st.warning("⚠️ No data available for the selected date.")

# ========================
# DETAILED ENVIRONMENT ANALYTICS
# ========================
elif page == "Detailed Analytics":
    st.title("📊 Detailed Environmental Analytics")

    if not filtered_df.empty:
        for col in ['MPUTemp', 'DHTHumidity', 'DHTTemp']:
            if col in filtered_df.columns:
                fig = px.line(filtered_df, x='Timestamp', y=col, title=f"{col} over Time")
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Full Data View"):
            st.dataframe(filtered_df[['Timestamp', 'MPUTemp', 'DHTHumidity', 'DHTTemp']])
    else:
        st.warning("⚠️ No data available for the selected date.")
