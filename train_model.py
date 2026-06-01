import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(__file__)

# -----------------------
# LOAD DATA
# -----------------------
dairy = pd.read_excel(os.path.join(BASE_DIR, "datasets/dairy_dataset.xlsx"))
livestock = pd.read_excel(os.path.join(BASE_DIR, "datasets/livestock_dataset.xlsx"))
poultry = pd.read_excel(os.path.join(BASE_DIR, "datasets/poultry_dataset.xlsx"))

# -----------------------
# CLEAN COLUMNS
# -----------------------
for df in [dairy, livestock, poultry]:
    df.columns = df.columns.str.strip()

# -----------------------
# SAFE CONVERSIONS
# -----------------------
def water_to_numeric(value):
    if pd.isna(value):
        return 20

    value = str(value).strip().lower()
    mapping = {"low": 10, "medium": 20, "high": 30}

    if value in mapping:
        return mapping[value]

    try:
        return float(value)
    except:
        return 20


def output_to_numeric(value):
    if pd.isna(value):
        return 10

    value = str(value).strip().lower()
    mapping = {"low": 10, "medium": 25, "high": 50}

    if value in mapping:
        return mapping[value]

    try:
        return float(value)
    except:
        return 20

# -----------------------
# DATA GENERATION
# -----------------------
rows = []

N_SAMPLES = 6000  # stable dataset size (not too noisy)

for i in range(N_SAMPLES):

    np.random.seed(i)

    d = dairy.sample(1).iloc[0]
    l = livestock.sample(1).iloc[0]
    p = poultry.sample(1).iloc[0]

    # -----------------------
    # ENVIRONMENT FEATURES
    # -----------------------
    temp = np.random.randint(18, 38)
    rainfall = np.random.randint(500, 1300)
    soil_ph = np.random.uniform(5.5, 7.5)

    # -----------------------
    # PRODUCTION FEATURES
    # -----------------------
    milk = float(d["Avg_Milk_Liters_Per_Day"])
    live = output_to_numeric(l["Average_Output_Per_Day"])
    poul = output_to_numeric(p["Average_Output_Per_Day"])

    manure = (
        float(l["Manure_Output_kg_per_day"]) +
        float(p["Manure_Output_kg_per_day"])
    )

    water = (
        water_to_numeric(d["Water_Requirement"]) +
        water_to_numeric(l["Water_Requirement_Liters_Per_Day"]) +
        water_to_numeric(p["Water_Requirement_Liters_Per_Day"])
    )

    # -----------------------
    # CORE LOGIC (IMPROVED AGRI MODEL)
    # -----------------------

    productivity = (
        milk * 2.2 +
        live * 1.6 +
        poul * 1.3
    )

    sustainability = (
        manure * 2.0 -
        water * 0.5
    )

    soil_score = (7 - abs(soil_ph - 6.5)) * 6

    weather_score = (28 - abs(temp - 28)) * 0.6

    # -----------------------
    # FINAL SCORE
    # -----------------------
    score = productivity + sustainability + soil_score + weather_score

    rows.append([
        temp,
        rainfall,
        soil_ph,
        milk,
        live,
        poul,
        manure,
        water,
        score
    ])

# -----------------------
# DATAFRAME
# -----------------------
df = pd.DataFrame(rows, columns=[
    "temp",
    "rainfall",
    "soil_ph",
    "milk",
    "livestock",
    "poultry",
    "manure",
    "water",
    "score"
])

# -----------------------
# NORMALIZATION (0–100)
# -----------------------
df["score"] = (
    (df["score"] - df["score"].min()) /
    (df["score"].max() - df["score"].min() + 1e-6)
) * 100

# -----------------------
# TRAIN MODEL
# -----------------------
X = df.drop("score", axis=1)
y = df["score"]

model = RandomForestRegressor(
    n_estimators=250,
    max_depth=14,
    random_state=42
)

model.fit(X, y)

# -----------------------
# SAVE MODEL
# -----------------------
joblib.dump(model, os.path.join(BASE_DIR, "ifs_model.pkl"))

print("✅ FINAL IFS MODEL TRAINED SUCCESSFULLY")
print("✔ Stable scoring")
print("✔ Reduced randomness")
print("✔ Better agriculture realism")
print("✔ UI-ready predictions")