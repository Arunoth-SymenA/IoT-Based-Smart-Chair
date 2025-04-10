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

# Load live or historical data
@st.cache_data
def load_data():
    return pd.read_csv("live_posture_data.csv")  # Replace with actual source, e.g. API or Firebase

# Page title
st.title("🪑 Smart Chair Sitting Posture Analytics")

# Load data
df = load_data()
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Calendar date selector
selected_date = st.date_input("Select a date", datetime.today().date())

# Filter data for selected date
filtered_df = df[df['Timestamp'].dt.date == selected_date]

# If there's data, proceed
if not filtered_df.empty:
    st.success(f"Data for {selected_date} loaded.")
    
    # Get last posture entry
    latest = filtered_df.iloc[-1]
    latest_posture = latest['Class_Label']
    correction = posture_corrections.get(latest_posture, "Unknown posture")

    # Display current posture and correction
    st.header(f"🧍 Current Posture: {latest_posture}")
    st.info(f"📝 Correction: {correction}")

    # Show temperature and humidity trends
    st.subheader("📊 Environment Analytics")
    cols_to_plot = ['MPUTemp', 'DHTHumidity', 'DHTTemp']
    for col in cols_to_plot:
        fig = px.line(filtered_df, x='Timestamp', y=col, title=f"{col} over Time")
        st.plotly_chart(fig, use_container_width=True)

    # Optional: Show entire data
    with st.expander("🔎 View Full Day's Data"):
        st.dataframe(filtered_df[['Timestamp', 'Class_Label', 'MPUTemp', 'DHTHumidity', 'DHTTemp']])

else:
    st.warning("No data available for this date.")