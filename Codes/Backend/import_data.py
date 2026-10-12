import pandas as pd
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://chairadmin:Chair2026@cluster0.rqofqc6.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["smart_chair_db"]
collection = db["sensor_readings"]

print("Reading file...")
df = pd.read_csv("chair_data.csv")

# Drop empty unnamed columns
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

print(f"Found {len(df)} rows")
print("Columns:", list(df.columns))

# Rename Class_Label to Posture_Label to match our app
df = df.rename(columns={"Class_Label": "Posture_Label"})

# Since there's no real timestamp, we'll assign April 10 2025 dates
# spread across the day so the calendar works
import numpy as np
base_date = datetime(2025, 4, 10, 8, 0, 0)  # starts at 8am
timestamps = [base_date + pd.Timedelta(minutes=i*2) for i in range(len(df))]
df['Timestamp'] = timestamps

# Also add temperature and sitting duration as simulated values
# since this training data doesn't have them
np.random.seed(42)
df['Temperature'] = np.random.uniform(24, 32, len(df)).round(1)
df['Sitting_Duration'] = np.random.randint(60, 300, len(df))
df['Alert_Sent'] = df['Posture_Label'].apply(lambda x: x == 'Bad')

print("Sample of data:")
print(df[['Timestamp', 'Posture_Label', 'Temperature', 'Sitting_Duration']].head())

# Clear old data
collection.delete_many({})

# Insert into MongoDB
records = df.to_dict(orient='records')
result = collection.insert_many(records)

print(f"\nSuccessfully inserted {len(result.inserted_ids)} records!")

# Show dates
pipeline = [
    {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$Timestamp"}}}}
]
dates = [d["_id"] for d in collection.aggregate(pipeline)]
print(f"Dates with data: {sorted(dates)}")

client.close()
print("Done!")
