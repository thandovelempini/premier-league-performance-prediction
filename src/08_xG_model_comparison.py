import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.linear_model import LinearRegression
from sklearn. metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

historical_df = pd.read_csv(PROCESSED_DATA_DIR / "fact_team_season_historical.csv")

print("\nFinal training dataset shape:", historical_df.shape)
print("\nMissing values in model inputs:")
print(
    historical_df[
        [
            "Shots_On_Target_Per_Match",
            "Shot_Conversion_Percentage",
            "Fouls_Per_Match",
            "Yellow_Cards_Per_Match",
            "Red_Cards_Per_Match",
            "xG_Per_Match",
            "xGA_Per_Match",
            "xG_Difference_Per_Match",
            "Points_Per_Match"
        ]
    ].isnull().sum()
)

# Define candidate feauture sets
feature_sets = {
    "Current model (shots/cards only)": [
        "Shots_On_Target_Per_Match",
        "Shot_Conversion_Percentage",
        "Fouls_Per_Match",
        "Yellow_Cards_Per_Match",
        "Red_Cards_Per_Match"
    ],
    "xG-augmented (shots/cards + xG difference)": [
        "Shots_On_Target_Per_Match",
        "Shot_Conversion_Percentage",
        "Fouls_Per_Match",
        "Yellow_Cards_Per_Match",
        "Red_Cards_Per_Match",
        "xG_Difference_Per_Match"
    ],
    "xG-only": [
        "xG_Per_Match",
        "xGA_Per_Match"
    ]
}

target = "Points_Per_Match"
y = historical_df[target]

# Compare models using same cross-validation as 03 file
cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results = []

for name, features in feature_sets.items():
    X = historical_df[features]

    model = LinearRegression()

    predictions = cross_val_predict(
        model,
        X,
        y,
        cv=cv
    )

    r2 = r2_score(y, predictions)
    mae = mean_absolute_error(y, predictions)
    rmse = mean_squared_error(y, predictions) ** 0.5

    # Express MAE/RMSE as season points so that comparison is interpretable at glance
    mae_season = mae * 38
    rmse_season = rmse * 38

    results.append({
        "Model": name,
        "Features": ", ".join(features),
        "R_Squared": round(r2, 4),
        "MAE_Per_Match": round(mae, 4),
        "RMSE_Per_Match": round(rmse, 4),
        "MAE_Season_Points": round(mae_season, 2),
        "RMSE_Season_Points": round(rmse_season, 2)
    })

comparison = pd.DataFrame(results)

print("\n" + "=" * 70)
print("Model Comparison: Current vs xG-Augmented vs xG-Only")
print("=" * 70)

print(
    comparison[
        [
            "Model",
            "R_Squared",
            "MAE_Season_Points",
            "RMSE_Season_Points"
        ]
    ].to_string(index=False)
)

print("\nFull feature lists:")
for row in results:
    print(f"- {row['Model']}: {row['Features']}")

# Fit final models on full data to inspect coefficients 
print("\n" + "=" * 70)
print("Coefficients (fit on full historical data, for reference only -")
print("R-Squared above is the trustworthy, cross-validated number)")
print("=" * 70)

for name, features in feature_sets.items():
    X = historical_df[features]
    model = LinearRegression()
    model.fit(X, y)

    print(f"\n{name}:")
    for feature, coef in zip(features, model.coef_):
        print(f"  {feature}: {coef:.6f}")
    print(f"  Intercept: {model.intercept_:.6f}")

comparison.to_csv(
    PROCESSED_DATA_DIR / "model_comparison_with_xg.csv",
    index=False
)