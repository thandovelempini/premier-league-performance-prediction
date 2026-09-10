import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Shot-level detail (location, body part, situation) which is only available for the current season
# No historical equivalent, solely for descriptive dashboard use, not for the points-prediction model
# See 08 file for that side of analysis

shots = pd.read_csv(PROCESSED_DATA_DIR / "pl_2026_27_shots_processed.csv")

# Standardise team names
 
team_name_mapping = {
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Newcastle": "Newcastle United",
    "Nott'm Forest": "Nottingham Forest",
    "Wolves": "Wolverhampton Wanderers"
}
 
understat_to_matchdata = {
    v: k for k, v in team_name_mapping.items()
}
 
shots["team"] = shots["team"].replace(understat_to_matchdata)

# Convert pitch coordinates into interpretable distance/angle 
# Understat convention: X in [0, 1] along pitch length (1 = attacking goal line)
# Y in [0, 1] across pitch width (0.5 = centre)
# Standard pitch dimensions used for conversion to metres

PITCH_LENGTH_M = 105
PITCH_WIDTH_M = 68
GOAL_WIDTH_M = 7.32

goal_x_m = PITCH_LENGTH_M
goal_y_m = PITCH_WIDTH_M / 2

shots["Shot_X_M"] = shots["X"] * PITCH_LENGTH_M
shots["Shot_Y_M"] = shots["Y"] * PITCH_WIDTH_M

shots["Shot_Distance_M"] = np.sqrt(
    (goal_x_m - shots["Shot_X_M"]) ** 2 +
    (goal_y_m - shots["Shot_Y_M"]) ** 2
)

# Angle available to the shooter, in degrees - a shot taken straight in front of goal has a wide angle,
# one from a tight sideline angle has a narrow one
# Standard formula using the two goalpost positions

post1_y = goal_y_m - (GOAL_WIDTH_M / 2)
post2_y = goal_y_m + (GOAL_WIDTH_M / 2)

def shot_angle(row):
    dx = goal_x_m - row["Shot_X_M"]
    dy1 = post1_y - row["Shot_Y_M"]
    dy2 = post2_y - row["Shot_Y_M"]

    angle1 = np.arctan2(dy1, dx)
    angle2 = np.arctan2(dy2, dx)

    return abs(np.degrees(angle2 - angle1))

shots["Shot_Angle_Degrees"] = shots.apply(shot_angle, axis=1)

print("\nShot distance and angle summary:")
print(
    shots[["Shot_Distance_M", "Shot_Angle_Degrees"]].describe()
)

# Team shot profile: body part breakdown
body_part_counts = (
    shots
    .groupby(["team", "shotType"])
    .size()
    .unstack(fill_value=0)
)

body_part_percentage = (
    body_part_counts
    .div(body_part_counts.sum(axis=1), axis=0) * 100
).round(1)

body_part_percentage.columns = [
    f"Pct_Shots_{col}" for col in body_part_percentage.columns
]

print("\nBody part breakdown by team (%):")
print(body_part_percentage)

# Team shot profile: situation breakdown
 
situation_counts = (
    shots
    .groupby(["team", "situation"])
    .size()
    .unstack(fill_value=0)
)
 
situation_percentage = (
    situation_counts
    .div(situation_counts.sum(axis=1), axis=0)
    * 100
).round(1)
 
situation_percentage.columns = [
    f"Pct_Shots_{col}" for col in situation_percentage.columns
]
 
print("\nSituation breakdown by team (%):")
print(situation_percentage)
 
# Team shot profile: location summary
 
location_summary = (
    shots
    .groupby("team")
    .agg(
        Avg_Shot_Distance_M=("Shot_Distance_M", "mean"),
        Avg_Shot_Angle_Degrees=("Shot_Angle_Degrees", "mean"),
        Pct_Shots_Inside_Box=(
            "Shot_Distance_M",
            lambda x: (x <= 16.5).mean() * 100
        )
    )
    .round(2)
)
 
print("\nShot location summary by team:")
print(location_summary)
 
# Combine into one team shot profile table
 
team_shot_profile = (
    body_part_percentage
    .join(situation_percentage)
    .join(location_summary)
    .reset_index()
    .rename(columns={"team": "Team"})
)
 
print("\n" + "=" * 70)
print("Team Shot Profile")
print("=" * 70)
print(team_shot_profile.to_string(index=False))
 
team_shot_profile.to_csv(
    PROCESSED_DATA_DIR / "team_shot_profile.csv",
    index=False
)
 
print("\nSaved team shot profile to team_shot_profile.csv")
 
# Shot-level export for Power BI shot maps
 
shot_map_export = shots[
    [
        "id",
        "match_id",
        "date",
        "team",
        "player",
        "team_side",
        "minute",
        "X",
        "Y",
        "Shot_X_M",
        "Shot_Y_M",
        "Shot_Distance_M",
        "Shot_Angle_Degrees",
        "shotType",
        "situation",
        "result",
        "is_goal",
        "xG",
        "high_xg_chance"
    ]
].rename(columns={
    "shotType": "Body_Part",
    "situation": "Situation",
    "result": "Result",
    "team": "Team",
    "player": "Player"
})
 
shot_map_export.to_csv(
    PROCESSED_DATA_DIR / "shot_map_export.csv",
    index=False
)
 
print("\nSaved shot-level Power BI export to shot_map_export.csv")
print("Shape:", shot_map_export.shape)


