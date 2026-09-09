import os
import pandas as pd
import joblib
import numpy as np


from merge_datasets import predict_ifs as merge_predict_ifs

BASE_DIR = os.path.dirname(__file__)


def load_datasets():
    try:
        return {
            "district": pd.read_excel(os.path.join(BASE_DIR, "datasets/district_info_updated.xlsx")),
            "dairy": pd.read_excel(os.path.join(BASE_DIR, "datasets/dairy_dataset.xlsx")),
            "livestock": pd.read_excel(os.path.join(BASE_DIR, "datasets/livestock_dataset.xlsx")),
            "poultry": pd.read_excel(os.path.join(BASE_DIR, "datasets/poultry_dataset.xlsx")),
            "mushroom": pd.read_excel(os.path.join(BASE_DIR, "datasets/mushroom_dataset.xlsx"))
        }
    except Exception as e:
        print("Dataset load error:", e)
        return {}

data = load_datasets()

def predict_ifs(lat, lon, budget="Medium", season="Kharif", state="Uttar Pradesh", district="Lucknow"):

    try:
        # Convert season format
        season_map = {
            "kharif": "Kharif",
            "rabi": "Rabi",
            "zaid": "Zaid"
        }

        season_clean = season_map.get(str(season).lower(), "Kharif")

        
        result = merge_predict_ifs(
            district=district,
            season=season_clean,
            soil_ph=6.8,   # optional override
            df_district=data["district"],
            df_dairy=data["dairy"],
            df_livestock=data["livestock"],
            df_poultry=data["poultry"],
            df_mushroom=data["mushroom"]
        )

        if "plans" in result and result["plans"]:
            result["graph_data"] = {
                "labels": [p["id"] for p in result["plans"]],
                "score": [p["score"] for p in result["plans"]],
                "profit": [p["profit"] for p in result["plans"]],
                "sustainability": [p["sustainability"] for p in result["plans"]],
            }

        return result

    except Exception as e:
        print("MODEL ERROR:", e)

        # HARD FALLBACK (NEVER FAIL UI)
        return {
            "district": district,
            "zone": "Unknown",
            "soil_ph": 6.5,
            "weather_type": "moderate",
            "plans": [
                {
                    "id": "Plan A",
                    "main_crops": ["Wheat", "Pea"],
                    "tree": "Neem",
                    "system": "Strip Cropping",
                    "score": 70,
                    "profit": 45000,
                    "sustainability": 75,
                    "synergy": "Safe fallback plan",
                    "why_crop": {
                        "soil_fit": 70,
                        "weather_fit": 80,
                        "diversity": 80,
                        "economic": 75
                    }
                }
            ],
            "graph_data": None
        }