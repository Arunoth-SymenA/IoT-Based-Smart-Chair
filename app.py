import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Posture correction dictionary
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

# Load and clean data from Google Sheet
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqPRHzgtmub8COW-9yQAu2qpYljeGQio6yXs5IKf5hm96dRGXsOipGGrLaH80h7AQVEbzb5lpTK9it/pub?output=csv"
    df = pd.read_csv(url)

    # Parse timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df.dropna(subset=['Timestamp'], inplace=True)

    # Replace -1 with last valid value for DHTHumidity
    if 'DHTHumidity' in df.columns:
        df['DHTHumidity'] = df['DHTHumidity'].replace(-1, pd.NA).ffill()

    return df

# Load the data
df = load_data()

# Page selector
st.set_page_config(page_title="Smart Chair Dashboard", layout="wide")
page = st.sidebar.selectbox("📄 Choose View", ["Live Analytics", "Detailed Analytics"])

# Date filter
selected_date = st.date_input("📅 Select a date", datetime.today().date())
filtered_df = df[df['Timestamp'].dt.date == selected_date]

# ------------------------------------
# 🟢 PAGE 1: Live Analytics
# ------------------------------------
if page == "Live Analytics":
    st.title("🪑 Smart Chair Posture - Live Analytics")

    if not filtered_df.empty:
        latest = filtered_df.iloc[-1]
        posture = latest.get('Class_Label', 'Unknown')
        correction = posture_corrections.get(posture, "No correction available.")
        temp = latest.get('MPUTemp', 'N/A')
        humidity = latest.get('DHTHumidity', 'N/A')

        st.header(f"🧍 Current Posture: `{posture}`")
        st.info(f"📝 Correction Tip: {correction}")

        st.subheader("🌡️ Current Environment")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Temperature", value=f"{temp} °C")
        with col2:
            st.metric(label="Environmental Humidity", value=f"{humidity} %")

        with st.expander("🔍 View Raw Posture Data"):
            st.dataframe(filtered_df[['Timestamp', 'Class_Label']])
    else:
        st.warning("⚠️ No data available for the selected date.")

# ------------------------------------
# 🔵 PAGE 2: Detailed Analytics
# ------------------------------------
elif page == "Detailed Analytics":
    st.title("📊 Detailed Environment Analytics")

    if not filtered_df.empty:
        for col in ['MPUTemp', 'DHTHumidity', 'DHTTemp']:
            if col in filtered_df.columns:
                st.subheader(f"{col} over Time")
                fig = px.line(filtered_df, x='Timestamp', y=col, title=col)
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Full Data View"):
            st.dataframe(filtered_df[['Timestamp', 'MPUTemp', 'DHTHumidity', 'DHTTemp']])
    else:
        st.warning("⚠️ No data available for the selected date.")
