import pandas as pd
import numpy as np
import joblib
import os

BASE_DIR = os.path.dirname(__file__)


try:
    model = joblib.load(os.path.join(BASE_DIR, "ifs_model.pkl"))
    print("ML Model Loaded")
except:
    model = None
    print("Model not found")

def safe_float(val):
    if pd.isna(val):
        return 10

    val = str(val).strip().lower()

    mapping = {
        "low": 10,
        "medium": 20,
        "high": 30
    }

    if val in mapping:
        return mapping[val]

    try:
        return float(val)
    except:
        return 10



def pick_row(df, col, value):
    df[col] = df[col].astype(str).str.lower().str.strip()
    value = str(value).lower().strip()

    match = df[df[col] == value]
    if not match.empty:
        return match.iloc[0]

    match = df[df[col].str.contains(value, na=False)]
    if not match.empty:
        return match.iloc[0]

    return df.iloc[0]



def bee_score(crops, flower):
    score = 0

    for c in crops:
        c = str(c).lower()
        if c in ["mustard", "sunflower"]:
            score += 20
        elif c in ["pumpkin", "cucumber"]:
            score += 15

    if str(flower).lower() in ["sunflower", "marigold"]:
        score += 20

    return score



def get_byproduct(crops, livestock, flower):
    crops_str = " ".join(crops).lower()

    if "rice" in crops_str:
        return "Paddy straw to livestock fodder"
    if "wheat" in crops_str:
        return "Wheat husk to cattle feed"
    if "mustard" in crops_str:
        return "Mustard oilcake to dairy feed"
    if "pumpkin" in crops_str:
        return "Vegetable waste to compost"
    if "sunflower" in flower.lower():
        return "Sunflower seeds to oil extraction"
    if "goat" in str(livestock).lower():
        return "Manure to organic fertilizer"

    return "General composting"



def get_flower(crops, seed):
    if any(c in ["Pumpkin", "Cucumber"] for c in crops):
        return "Sunflower"

    if any(c in ["Rice", "Soybean"] for c in crops):
        return "Marigold"

    return "Hibiscus" if seed % 2 else "Marigold"

def pollination_score(crops, flower, bee):
    score = 0

    crops_str = " ".join(crops).lower()

    # crop pollination value
    if "pumpkin" in crops_str or "cucumber" in crops_str:
        score += 30
    if "soybean" in crops_str:
        score += 20
    if "rice" in crops_str:
        score += 10

    # flower impact
    if flower in ["Sunflower", "Marigold"]:
        score += 25
    elif flower == "Hibiscus":
        score += 15

    # bee system impact
    if bee == "Apis Mellifera":
        score += 30
    elif bee != "Not Required":
        score += 15

    return score

def generate_strategy(temp, rainfall, district, strategy):

    seed = abs(hash(district)) % 100

    if rainfall > 1000:
        base = ["Rice", "Soybean"]
    elif rainfall > 800:
        base = ["Maize", "Black Gram"]
    elif temp > 30:
        base = ["Bajra", "Jowar"]
    elif seed % 2 == 0:
        base = ["Wheat", "Mustard"]
    else:
        base = ["Wheat", "Pea"]

    if strategy == "BALANCED":
        base[1] = "Lentil"
    elif strategy == "ECO":
        base[1] = "Pumpkin"

    # TREE
    if rainfall > 900:
        tree = "Mango"
    elif seed % 3 == 0:
        tree = "Guava"
    else:
        tree = "Neem"

    flower = get_flower(base, seed)

    bee_val = bee_score(base, flower)
    bee = "Apis Mellifera" if bee_val > 20 else "Not Required"

    return base, tree, flower, bee



def predict_ifs(
    district,
    season,
    soil_ph,
    df_district,
    df_dairy,
    df_livestock,
    df_poultry,
    df_mushroom
):

    try:
        loc = pick_row(df_district, "District", district)

        temp = safe_float(loc.get("Avg_Temp", 28))
        rainfall = safe_float(loc.get("Rainfall", 800))
        zone = loc.get("Zone", "Unknown")

        results = []
        strategies = ["INTENSIVE", "BALANCED", "ECO"]

        for i, strategy in enumerate(strategies):

           
            crops, tree, flower, bee = generate_strategy(
                temp, rainfall, district, strategy
            )

            idx = (i + abs(hash(district))) % len(df_dairy)

            dairy = df_dairy.iloc[idx % len(df_dairy)]
            livestock = df_livestock.iloc[idx % len(df_livestock)]
            poultry = df_poultry.iloc[idx % len(df_poultry)]
            mushroom = df_mushroom.iloc[idx % len(df_mushroom)]

           
            milk = safe_float(dairy.get("Avg_Milk_Liters_Per_Day", 5))
            live = safe_float(str(livestock.get("Average_Output_Per_Day", "2")).split()[0])
            poul = safe_float(str(poultry.get("Average_Output_Per_Day", "2")).split()[0])

            manure = safe_float(livestock.get("Manure_Output_kg_per_day", 5)) + \
                     safe_float(poultry.get("Manure_Output_kg_per_day", 2))

            water = safe_float(dairy.get("Water_Requirement", 50)) + \
                    safe_float(livestock.get("Water_Requirement_Liters_Per_Day", 30))

            income = milk*2.5 + live*1.8 + poul*1.5
            sustainability = max(0, manure*2.2 - water*0.6)

           
            features = np.array([[temp, rainfall, soil_ph, milk, live, poul, manure, water]])

            if model:
                score = float(model.predict(features)[0])
            else:
                score = income + sustainability

            
            byproduct = get_byproduct(crops, livestock.get("Breed", ""), flower)

           
            poll_score = pollination_score(crops, flower, bee)

           
            results.append({
                "id": f"Plan {chr(65+i)}",
                "strategy": strategy,

                "crops": crops,
                "tree": tree,
                "flower": flower,
                "bee": bee,

                "dairy": dairy.get("Animal_Breed", "Cow"),
                "livestock": livestock.get("Breed", "Goat"),
                "poultry": poultry.get("Breed", "Chicken"),
                "mushroom": mushroom.get("Name", "Button"),

                "byproduct": byproduct,

                "score": round(score, 2),

                # IMPORTANT NEW METRIC
                "pollination_score": round(poll_score, 2),

                "metrics": {
                    "income": round(income, 2),
                    "sustainability": round(sustainability, 2),
                    "environment": 0,
                    "bee_impact": 0
                }
            })

        
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return {
            "district": district,
            "zone": zone,
            "season": season,
            "plans": results
        }

    except Exception as e:
        print("ENGINE ERROR:", e)
        return {"plans": []}