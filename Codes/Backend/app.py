from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
import pickle
import pandas as pd
from datetime import datetime, timedelta

# SETUP
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
jwt = JWTManager(app)

# DATABASE
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DATABASE_NAME")]
users_col = db["users"]
readings_col = db["sensor_readings"]

# LOAD ML MODEL
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    print("ML model loaded successfully")
except Exception as e:
    print(f"Could not load model: {e}")
    model = None

# HELPER FUNCTIONS
def calculate_posture_score(df):
    if len(df) == 0:
        return 0
    counts = df["Posture_Label"].value_counts()
    good = counts.get("A", 0)
    return round((good / len(df)) * 100)

def group_posture_labels(df):
    """Group all labels into Good, Bad, Neutral."""
    grouped = {"Good": 0, "Bad": 0, "Neutral": 0}
    for label, count in df["Posture_Label"].value_counts().items():
        if label == "A":
            grouped["Good"] += count
        elif label == "B":
            grouped["Bad"] += count
        else:
            grouped["Neutral"] += count
    # Remove zero counts
    return {k: v for k, v in grouped.items() if v > 0}

def get_recommendations(df):
    recommendations = []
    score = calculate_posture_score(df)
    avg_temp = df["Temperature"].mean() if "Temperature" in df.columns else 25
    total_mins = df["Sitting_Duration"].sum() / 60 if "Sitting_Duration" in df.columns else 0

    if score >= 80:
        recommendations.append({
            "type": "success",
            "icon": "✅",
            "title": "Excellent Posture!",
            "text": "You maintained great posture today. Keep it up!"
        })
    elif score >= 50:
        recommendations.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Posture Needs Attention",
            "text": "Your posture was okay but could be better. Try to keep your back fully against the chair."
        })
    else:
        recommendations.append({
            "type": "error",
            "icon": "❌",
            "title": "Poor Posture Detected",
            "text": "You slouched frequently. Sit with your back straight and feet flat on the floor."
        })

    if total_mins > 120:
        recommendations.append({
            "type": "warning",
            "icon": "🚶",
            "title": "Too Much Sitting",
            "text": f"You sat for {round(total_mins)} minutes. Take a 5 minute walk every hour."
        })

    if avg_temp > 32:
        recommendations.append({
            "type": "warning",
            "icon": "🌡️",
            "title": "High Temperature",
            "text": f"Seat temperature averaged {round(avg_temp, 1)}C. Improve airflow around your chair."
        })
    else:
        recommendations.append({
            "type": "success",
            "icon": "🌤️",
            "title": "Comfortable Temperature",
            "text": f"Temperature was a comfortable {round(avg_temp, 1)}C. Good for focused work."
        })

    return recommendations

def get_hourly_breakdown(df):
    if "Timestamp" not in df.columns:
        return []
    df = df.copy()
    df["hour"] = pd.to_datetime(df["Timestamp"]).dt.hour
    hourly = []
    for hour in sorted(df["hour"].unique()):
        subset = df[df["hour"] == hour]
        counts = subset["Posture_Label"].value_counts()
        hourly.append({
            "hour": int(hour),
            "label": f"{int(hour)}:00",
            "good": int(counts.get("A", 0)),
            "bad": int(counts.get("B", 0)),
            "neutral": int(counts.get("C", 0)),
            "total": len(subset)
        })
    return hourly

# AUTH ROUTES
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    if not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if users_col.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())

    users_col.insert_one({
        "name": data["name"],
        "email": data["email"],
        "password": hashed,
        "created_at": datetime.now()
    })

    return jsonify({"message": "Account created! Please log in."}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = users_col.find_one({"email": data["email"]})

    if not user or not bcrypt.checkpw(data["password"].encode("utf-8"), user["password"]):
        return jsonify({"error": "Incorrect email or password"}), 401

    token = create_access_token(identity=str(user["_id"]))

    return jsonify({
        "token": token,
        "name": user["name"],
        "email": user["email"]
    }), 200


# DATA ROUTES
@app.route("/analytics/<date>", methods=["GET"])
@jwt_required()
def get_analytics(date):
    try:
        start = datetime.strptime(date, "%Y-%m-%d")
        end = start + timedelta(days=1)

        readings = list(readings_col.find(
            {"Timestamp": {"$gte": start, "$lt": end}},
            {"_id": 0}
        ))

        if not readings:
            return jsonify({"error": f"No data for {date}"}), 404

        df = pd.DataFrame(readings)

        analytics = {
            "date": date,
            "total_readings": len(readings),
            "posture_counts": group_posture_labels(df),
            "posture_score": calculate_posture_score(df),
            "avg_temperature": round(df["Temperature"].mean(), 1),
            "max_temperature": round(df["Temperature"].max(), 1),
            "min_temperature": round(df["Temperature"].min(), 1),
            "total_sitting_minutes": round(df["Sitting_Duration"].sum() / 60, 1),
            "avg_flex_angle": round(df["AccelX"].mean(), 1) if "AccelX" in df.columns else 0,
            "alerts_sent": int(df["Alert_Sent"].sum()) if "Alert_Sent" in df.columns else 0,
            "hourly_posture": get_hourly_breakdown(df),
            "recommendations": get_recommendations(df),
        }

        return jsonify(analytics), 200

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/available-dates", methods=["GET"])
@jwt_required()
def get_available_dates():
    try:
        pipeline = [
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$Timestamp"}}}},
            {"$sort": {"_id": 1}}
        ]
        dates = [doc["_id"] for doc in readings_col.aggregate(pipeline)]
        return jsonify({"dates": dates}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/receive-data", methods=["POST"])
def receive_iot_data():
    data = request.json
    data["Timestamp"] = datetime.now()

    if model:
        try:
            features = [[
                data.get("FSR0", 0), data.get("FSR1", 0),
                data.get("FSR2", 0), data.get("FSR3", 0),
                data.get("FSR4", 0), data.get("FSR5", 0),
                data.get("FSR6", 0), data.get("FSR7", 0),
                data.get("FSR8", 0), data.get("FSR9", 0),
                data.get("FSR10", 0), data.get("FSR11", 0),
                data.get("AccelX", 0), data.get("AccelY", 0),
                data.get("AccelZ", 0), data.get("GyroX", 0),
                data.get("GyroY", 0), data.get("GyroZ", 0)
            ]]
            prediction = model.predict(features)[0]
            data["Posture_Label"] = str(prediction)
            data["Alert_Sent"] = (prediction == "B")
        except Exception as e:
            data["Posture_Label"] = "Unknown"
            data["Alert_Sent"] = False

    readings_col.insert_one(data)
    return jsonify({
        "status": "saved",
        "posture": data.get("Posture_Label", "Unknown")
    }), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running", "message": "Smart Chair API is live!"}), 200


# START
if __name__ == "__main__":
    print("Starting Smart Chair Backend...")
    print("Running on http://localhost:5000")
    app.run(debug=True, port=5000, host="0.0.0.0")