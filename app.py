import os
import pandas as pd
import requests
from flask import Flask, render_template, request, jsonify

from merge_datasets import predict_ifs

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)


def load_datasets():
    try:
        datasets = {
            "district": pd.read_excel(os.path.join(BASE_DIR, "datasets/district_info_updated.xlsx")),
            "dairy": pd.read_excel(os.path.join(BASE_DIR, "datasets/dairy_dataset.xlsx")),
            "livestock": pd.read_excel(os.path.join(BASE_DIR, "datasets/livestock_dataset.xlsx")),
            "poultry": pd.read_excel(os.path.join(BASE_DIR, "datasets/poultry_dataset.xlsx")),
            "mushroom": pd.read_excel(os.path.join(BASE_DIR, "datasets/mushroom_dataset.xlsx"))
        }

        print(" All datasets loaded successfully")
        return datasets

    except Exception as e:
        print(" Dataset load error:", e)
        return {}

data = load_datasets()


def clean_location_df(df):
    df.columns = df.columns.str.strip()
    df["District"] = df["District"].astype(str).str.lower().str.strip()
    df["State"] = df["State"].astype(str).str.lower().str.strip()
    return df

if "district" in data:
    data["district"] = clean_location_df(data["district"])


def get_location_info(state, district):
    try:
        df = data["district"]

        state = str(state).lower().strip()
        district = str(district).lower().strip()

        print(" Searching:", state, district)

        row = df[
            (df["District"] == district) &
            (df["State"] == state)
        ]

        if row.empty:
            print(" Exact match not found, trying partial match...")
            row = df[df["District"].str.contains(district, na=False)]

        if not row.empty:
            row = row.iloc[0]
            return float(row["Latitude"]), float(row["Longitude"]), row.get("Zone", "Unknown")

        print(" Location fallback used")
        return 26.85, 80.94, "Unknown"

    except Exception as e:
        print(" Location error:", e)
        return 26.85, 80.94, "Unknown"


def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

        res = requests.get(url, timeout=5)
        data = res.json()

        weather = data.get("current_weather", {})

        return {
            "temperature": weather.get("temperature", 28),
            "windspeed": weather.get("windspeed", 10),
            "weathercode": weather.get("weathercode", 0)
        }

    except Exception as e:
        print("❌ Weather API error:", e)
        return {
            "temperature": 28,
            "windspeed": 10,
            "weathercode": 0
        }


def get_soil_data(district):
    return {
        "ph": 6.5 + (hash(district) % 10) * 0.1,
        "moisture": 50 + (hash(district) % 30),
        "fertility": 60 + (hash(district) % 25)
    }


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/recommend")
def recommend():
    return render_template("recommend.html")

@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/get_recommendation", methods=["POST"])
def get_recommendation():

    try:
        req = request.get_json()

        state = req.get("state", "Uttar Pradesh")
        district = req.get("district", "Lucknow")
        season = req.get("season", "Kharif")
        budget = req.get("budget", "Medium")

        print("\n🚀 REQUEST:", state, district, season, budget)

       
        lat, lon, zone = get_location_info(state, district)

        
        weather = get_weather(lat, lon)

       
        soil = get_soil_data(district)

        
        try:
            result = predict_ifs(
                district=district,
                season=season,
                soil_ph=soil["ph"],
                df_district=data.get("district"),
                df_dairy=data.get("dairy"),
                df_livestock=data.get("livestock"),
                df_poultry=data.get("poultry"),
                df_mushroom=data.get("mushroom")
            )

            print(" MODEL OUTPUT:", result)
            print(" RESULT FROM ENGINE:", result)

        except Exception as model_error:
            print(" MODEL ERROR:", model_error)
            result = None

        
        if not result or not result.get("plans"):
            print("⚠ Using fallback plans")

            result = {
                "plans": [
                    {
                        "id": "Plan A",
                        "crops": ["Rice", "Soybean"],
                        "tree": "Mango",
                        "flower": "Sunflower",
                        "dairy": "Cow",
                        "livestock": "Goat",
                        "poultry": "Chicken",
                        "mushroom": "Button Mushroom",
                        "score": 75,
                        "metrics": {"income": 60, "sustainability": 65}
                    },
                    {
                        "id": "Plan B",
                        "crops": ["Maize", "Black Gram"],
                        "tree": "Guava",
                        "flower": "Marigold",
                        "dairy": "Buffalo",
                        "livestock": "Sheep",
                        "poultry": "Broiler",
                        "mushroom": "Oyster",
                        "score": 70,
                        "metrics": {"income": 55, "sustainability": 70}
                    },
                    {
                        "id": "Plan C",
                        "crops": ["Bajra", "Cowpea"],
                        "tree": "Neem",
                        "flower": "Hibiscus",
                        "dairy": "Cow",
                        "livestock": "Goat",
                        "poultry": "Desi Chicken",
                        "mushroom": "Milky Mushroom",
                        "score": 65,
                        "metrics": {"income": 50, "sustainability": 80}
                    }
                ]
            }

        
        graph_data = {
            "labels": [p["id"] for p in result["plans"]],
            "datasets": [
                {
                    "label": "Score",
                    "data": [p["score"] for p in result["plans"]],
                    "borderColor": "#1b5e20",
                    "tension": 0.4
                },
                {
                    "label": "Income",
                    "data": [p["metrics"].get("income", 0) for p in result["plans"]],
                    "borderColor": "#f9a825",
                    "tension": 0.4
                },
                {
                    "label": "Sustainability",
                    "data": [p["metrics"].get("sustainability", 0) for p in result["plans"]],
                    "borderColor": "#2e7d32",
                    "tension": 0.4
                }
            ]
        }

        
        return jsonify({
    "location": {
        "state": state,
        "district": district,
        "zone": zone
    },
    "weather": weather,
    "soil": soil,
    "plans": result["plans"],
    "graph": graph_data
})

    except Exception as e:
        print(" API ERROR:", e)

        return jsonify({
            "error": "Server crashed",
            "plans": []
        }), 500



if __name__ == "__main__":
    app.run(debug=True, port=5000)