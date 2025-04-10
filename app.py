import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Correction messages dictionary
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

# Load data from public Google Sheet
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqPRHzgtmub8COW-9yQAu2qpYljeGQio6yXs5IKf5hm96dRGXsOipGGrLaH80h7AQVEbzb5lpTK9it/pub?output=csv"
    df = pd.read_csv(url)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df.dropna(subset=['Timestamp'], inplace=True)  # Remove rows with invalid timestamps
    return df

# Streamlit Page Title
st.set_page_config(page_title="Smart Chair Dashboard", layout="wide")
st.title("🪑 Smart Chair Sitting Posture Analytics")

# Load and display data
df = load_data()

# Date selection from calendar
selected_date = st.date_input("📅 Select a date", datetime.today().date())

# Filter data for selected date
filtered_df = df[df['Timestamp'].dt.date == selected_date]

# Display results
if not filtered_df.empty:
    st.success(f"✅ Data loaded for {selected_date}!")

    # Current Posture
    latest = filtered_df.iloc[-1]
    posture = latest.get('Class_Label', 'Unknown')
    correction = posture_corrections.get(posture, "No correction available for this label.")

    st.header(f"🧍 Current Posture Detected: `{posture}`")
    st.info(f"📝 Correction Tip: {correction}")

    # Environmental Graphs
    st.subheader("📊 Environment Metrics for the Day")

    col1, col2, col3 = st.columns(3)
    with col1:
        fig1 = px.line(filtered_df, x='Timestamp', y='MPUTemp', title='MPU Temperature')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.line(filtered_df, x='Timestamp', y='DHTHumidity', title='DHT Humidity')
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        fig3 = px.line(filtered_df, x='Timestamp', y='DHTTemp', title='DHT Temperature')
        st.plotly_chart(fig3, use_container_width=True)

    # Full data
    with st.expander("🔍 View Full Data for Selected Date"):
        st.dataframe(filtered_df[['Timestamp', 'Class_Label', 'MPUTemp', 'DHTHumidity', 'DHTTemp']])

else:
    st.warning("⚠️ No data available for the selected date.")
