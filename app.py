import streamlit as st
from datetime import datetime
import pandas as pd
import joblib
import plotly.express as px
import numpy as np

# ✅ First Streamlit config
st.set_page_config(
    page_title="Design and Implementation of IoT and ML based Smart Chair for Health Monitoring and Recommendations",
    layout="wide"
)

# Sidebar dropdown
page = st.sidebar.selectbox("📄 Select Page", ["🏠 Home", "📊 Live Analytics", "🌡️ Detailed Analytics"])

# Expandable Problem Statement + Proposed Solution
with st.sidebar.expander("💡 Project Context"):
    st.markdown("### **Problem Statement**")
    st.write("""
    The modern lifestyle's shift towards prolonged sedentary activities... There is a pressing need for an intelligent system...
    """)
    st.markdown("### **Proposed Solution**")
    st.write("""
    To address these challenges, we propose the development of an **IoT-based Smart Chair system integrated with Machine Learning capabilities**...
    """)

# HOME PAGE
if page == "🏠 Home":
    st.title("Design and Implementation of IoT and ML based Smart Chair for Health Monitoring and Recommendations")

    st.markdown("## 🪑 **Smart Chair: IoT & ML-Powered Health Monitoring System**")
    st.markdown("**Welcome to the Smart Chair Platform! 🧠💺📊**")

    st.image("https://cdn.pixabay.com/photo/2018/01/15/07/51/smart-3087393_960_720.jpg", caption="Smart Chair Concept", use_column_width=True)

    st.markdown("""
    Our mission is to revolutionize how we sit by transforming traditional seating into a health-conscious experience...
    """)

    st.markdown("### 🔧 **Technologies Used**")
    st.markdown("- **Internet of Things (IoT)**\n- **Machine Learning Models**\n- **Streamlit – Frontend Dashboard**\n- **Google Sheets – Real-Time Cloud Storage**")

    st.markdown("## ⚙️ **How It Works**")
    st.markdown("### **1. Data Collection**")
    st.markdown("""
    The chair continuously collects sensor data including:
    - Seating pressure from **12 FSR sensors**
    - **Posture tilt and movement** using **MPU-6050**
    - **Ambient temperature & humidity** via the **DHT22**
    - **Posture status feedback** using **LED indicators**
    """)

    st.markdown("### **2. Real-Time Analysis**")
    st.markdown("Navigate to the **Posture Monitor** or **Daily Analytics** pages to view live posture data and sensor trends...")

    st.markdown("### **3. Predictive Insights**")
    st.markdown("Our system uses a pre-trained ML model to predict posture type, evaluate posture quality, and generate insights...")

    st.markdown("### **4. Feedback & Recommendations**")
    st.markdown("- **Visual LED alerts**, **Mobile app notifications**, **Personalized Streamlit insights**, **Long-term ergonomic suggestions**")

    st.markdown("## 🧩 **Components and Flow**")
    st.image("https://cdn.pixabay.com/photo/2017/03/03/14/52/technology-2111326_960_720.jpg", caption="System Architecture", use_column_width=True)
    st.markdown("""
    - **ESP32 Microcontroller**: Collects and transmits sensor data
    - **12× Force Sensitive Resistors (FSRs)**: Monitor seat and back pressure
    - **16-Channel Multiplexer**, **MPU-6050**, **DHT22 Sensor**, **LEDs**, **Power Supply**
    """)

    st.markdown("## 🌟 **Why Choose Our Smart Chair?**")
    st.markdown("""
    ✅ **Health-Focused**  
    ✅ **Live Feedback**  
    ✅ **Non-Invasive**  
    ✅ **Data-Driven**  
    ✅ **User-Centric**
    """)

    st.markdown("## 🚀 **Get Started**")
    st.markdown("Head to the **📊 Live Analytics** page in the sidebar!")

    st.markdown("## 🙋‍♂️ **About Us**")
    st.markdown("""
    Learn more about the vision behind this smart ergonomic solution and the team that made it possible.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github)](https://github.com/yourhandle)")
    with col2:
        st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/yourhandle)")

# DATA FUNCTIONS & MODEL
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqPRHzgtmub8COW-9yQAu2qpYljeGQio6yXs5IKf5hm96dRGXsOipGGrLaH80h7AQVEbzb5lpTK9it/pub?output=csv"
    df = pd.read_csv(url)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df.dropna(subset=['Timestamp'], inplace=True)
    df['DHTHumidity'] = df['DHTHumidity'].replace(-1, pd.NA).ffill()
    return df

@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

model = load_model()
model_features = ['FSR0','FSR1','FSR2','FSR3','FSR4','FSR5','FSR6','FSR7','FSR8','FSR9','FSR10','FSR11','AccelX','AccelY','AccelZ','GyroX','GyroY','GyroZ']
posture_quality_map = {'A':'Good','C':'Average','D':'Average','E':'Average','F':'Average','G':'Average',
                       'B':'Bad','H':'Bad','I':'Bad','J':'Bad','K':'Bad','L':'Bad','M':'Bad','N':'Bad',
                       'O':'Bad','P':'Bad','Q':'Bad','R':'Bad','S':'Bad','T':'Bad'}

# PAGE: LIVE ANALYTICS
if page == "📊 Live Analytics":
    df = load_data()
    selected_date = st.date_input("📅 Select a date", datetime.today().date())
    filtered_df = df[df['Timestamp'].dt.date == selected_date]

    if not filtered_df.empty:
        X = filtered_df[model_features]
        filtered_df['Predicted_Label'] = model.predict(X)
        filtered_df['Posture_Quality'] = filtered_df['Predicted_Label'].map(posture_quality_map)
        filtered_df['Hour'] = filtered_df['Timestamp'].dt.hour
        latest = filtered_df.iloc[-1]
        latest_posture = latest['Predicted_Label']

        st.title("🪑 Smart Chair Posture - Daily Posture Analytics")
        st.subheader("🧍 Current Posture")
        st.success(f"**Posture:** `{latest_posture}`")
        st.metric("Temperature", f"{latest['MPUTemp']} °C")
        st.metric("Humidity", f"{latest['DHTHumidity']} %")

        # Graph 1: Bar - posture frequency
        fig1 = px.bar(filtered_df['Predicted_Label'].value_counts().reset_index(), x='index', y='Predicted_Label', title="Posture Count", labels={"index":"Posture","Predicted_Label":"Count"})
        st.plotly_chart(fig1, use_container_width=True)

        # Graph 2: Line - good/avg/bad
        quality_numeric = {'Good': 2, 'Average': 1, 'Bad': 0}
        filtered_df['Quality_Score'] = filtered_df['Posture_Quality'].map(quality_numeric)
        fig2 = px.line(filtered_df, x='Timestamp', y='Quality_Score', title="Posture Quality Timeline")
        fig2.update_yaxes(tickvals=[0, 1, 2], ticktext=['Bad', 'Average', 'Good'])
        st.plotly_chart(fig2, use_container_width=True)

        # Graph 3: Pie - posture quality share
        fig3 = px.pie(filtered_df, names='Posture_Quality', title="Posture Quality Share")
        st.plotly_chart(fig3, use_container_width=True)

        # Graph 4: Bar - time spent per posture
        filtered_df['TimeSpent'] = filtered_df['Timestamp'].diff().dt.total_seconds().fillna(0)
        time_spent = filtered_df.groupby('Predicted_Label')['TimeSpent'].sum().reset_index()
        fig4 = px.bar(time_spent, x='Predicted_Label', y='TimeSpent', title="Time Spent in Each Posture (seconds)")
        st.plotly_chart(fig4, use_container_width=True)

        # Graph 5: Heatmap - postures per hour
        hourly = filtered_df.groupby(['Hour', 'Predicted_Label']).size().reset_index(name='Count')
        fig5 = px.density_heatmap(hourly, x='Hour', y='Predicted_Label', z='Count', color_continuous_scale="Viridis", title="Posture Frequency by Hour")
        st.plotly_chart(fig5, use_container_width=True)

        # Stat 6: Transition count
        filtered_df['Shifted'] = filtered_df['Predicted_Label'].shift()
        filtered_df['Changed'] = filtered_df['Predicted_Label'] != filtered_df['Shifted']
        st.info(f"🔁 You changed posture **{int(filtered_df['Changed'].sum())} times** today.")
    else:
        st.warning("⚠️ No data available for this date.")

# PAGE: DETAILED ANALYTICS
elif page == "🌡️ Detailed Analytics":
    df = load_data()
    selected_date = st.date_input("📅 Select a date", datetime.today().date(), key="detail_date")
    filtered_df = df[df['Timestamp'].dt.date == selected_date]
    st.title("📊 Environmental Sensor Analytics")

    if not filtered_df.empty:
        for col in ['MPUTemp', 'DHTHumidity', 'DHTTemp']:
            fig = px.line(filtered_df, x='Timestamp', y=col, title=f"{col} over Time")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(filtered_df[['Timestamp', 'MPUTemp', 'DHTHumidity', 'DHTTemp']])
    else:
        st.warning("⚠️ No environmental data for this date.")
