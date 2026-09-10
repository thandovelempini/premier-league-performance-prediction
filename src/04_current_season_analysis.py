import pandas as pd 

current_matches = pd.read_csv("data/raw/season-data/season-2627.csv")

print("Dataset shape:")
print(current_matches.shape)

print("\nColumns:")
print(current_matches.columns.tolist())

print("First 5 rows:")
print(current_matches.head())

print("\nData types and missing values:")
current_matches.info()

print("\nMissing values:")
print(current_matches.isnull().sum())

# Select columns relevant to the analysis
current_matches = current_matches[
    [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR",
        "HS",
        "AS",
        "HST",
        "AST",
        "HF",
        "AF",
        "HC",
        "AC",
        "HY",
        "AY",
        "HR",
        "AR"
    ]
]

print("\nSelected dataset:")
print(current_matches.head())

print("\nSelected columns:")
print(current_matches.columns.tolist())

# Check number of unique teams
teams = set(current_matches["HomeTeam"]) | set(current_matches["AwayTeam"])

print("\nNumber of unique teams:")
print(len(teams))

print("\nTeams:")
print(sorted(teams))

# Check appearances per team
home_counts = current_matches["HomeTeam"].value_counts()
away_counts = current_matches["AwayTeam"].value_counts()

team_appearances = home_counts.add(
    away_counts,
    fill_value=0
)

print("\nTeam appearances:")
print(team_appearances.sort_index())

print("\nTeams not appearing exactly once:")
print(team_appearances[team_appearances != 1])

# Create home team statistics 
home_stats = pd.DataFrame({
    "Team": current_matches["HomeTeam"],
    "Matches_Played": 1,
    "Wins": (current_matches["FTR"] == "H").astype(int),
    "Draws": (current_matches["FTR"] == "D").astype(int),
    "Losses": (current_matches["FTR"] == "A").astype(int),
    "Points": current_matches["FTR"].map({
        "H": 3,
        "D": 1,
        "A": 0
    }),
    "Goals_Scored": current_matches["FTHG"],
    "Goals_Conceded": current_matches["FTAG"],
    "Shots": current_matches["HS"],
    "Shots_On_Target": current_matches["HST"],
    "Fouls": current_matches["HF"],
    "Corners": current_matches["HC"],
    "Yellow_Cards": current_matches["HY"],
    "Red_Cards": current_matches["HR"]
})

# Create away team statistics 
away_stats = pd.DataFrame({
    "Team": current_matches["AwayTeam"],
    "Matches_Played": 1,
    "Wins": (current_matches["FTR"] == "A").astype(int),
    "Draws": (current_matches["FTR"] == "D").astype(int),
    "Losses": (current_matches["FTR"] == "H").astype(int),
    "Points": current_matches["FTR"].map({
        "H": 0,
        "D": 1,
        "A": 3
    }),
    "Goals_Scored": current_matches["FTAG"],
    "Goals_Conceded": current_matches["FTHG"],
    "Shots": current_matches["AS"],
    "Shots_On_Target": current_matches["AST"],
    "Fouls": current_matches["AF"],
    "Corners": current_matches["AC"],
    "Yellow_Cards": current_matches["AY"],
    "Red_Cards": current_matches["AR"]
})

# Combine home away statistics
current_team_stats = pd.concat(
    [home_stats, away_stats],
    ignore_index=True
)

# Aggregate match-level rows into one row per team
current_team_stats = (
    current_team_stats
    .groupby("Team", as_index=False)
    .sum(numeric_only=True)
)

# Calculate additional metrics

current_team_stats["Goal_Difference"] = (
    current_team_stats["Goals_Scored"] -
    current_team_stats["Goals_Conceded"]
)

current_team_stats["Shot_Conversion_Percentage"] = (
    current_team_stats["Goals_Scored"] / current_team_stats["Shots"]
) * 100

current_team_stats["Shot_On_Target_Conversion_Percentage"] = (
    current_team_stats["Goals_Scored"] / current_team_stats["Shots_On_Target"].replace(0, pd.NA)
) * 100

current_team_stats["Shot_On_Target_Conversion_Percentage"] = (
    current_team_stats["Shot_On_Target_Conversion_Percentage"].fillna(0)
)

# Sort by points
current_team_stats = current_team_stats.sort_values(
    ["Points", "Goal_Difference", "Goals_Scored"],
    ascending=False
).reset_index(drop=True)

print("\nCurrent Season Team Statistics:")
print(current_team_stats)

# Validate dataset
print("\nDataset shape:")
print(current_team_stats.shape)

print("\nMissing values:")
print(current_team_stats.isnull().sum())

print("\nTeams with a Matches_Played total that does not match their actual fixture count:")
print(
    current_team_stats[
        current_team_stats["Team"].map(team_appearances) != 
        current_team_stats["Matches_Played"]
    ]
)

print("\nInvalid points calculations:")
print(
    current_team_stats[
        current_team_stats["Points"] != (
            current_team_stats["Wins"] * 3 +
            current_team_stats["Draws"]
        )
    ]
)

# HISTORICAL TEAM-SEASON METRICS

# Read the pre-built historical fact table (built by
# build_historical_fact.py) instead of rebuilding the xG merge
# here - keeping one source of truth for this data avoids the
# kind of silent season-mismatch bug this project hit earlier,
# where two independent copies of this logic could drift apart.

historical_df = pd.read_csv(
    "data/processed/fact_team_season_historical.csv"
)

print("\nHistorical per-match metrics:")
print(
    historical_df[
        [ 
            "Season",
            "Team",
            "Shots_Per_Match",
            "Shots_On_Target_Per_Match",
            "Fouls_Per_Match",
            "Yellow_Cards_Per_Match",
            "Red_Cards_Per_Match",
            "Shot_Conversion_Percentage",
            "xG_Difference_Per_Match",
            "Points_Per_Match"
        ]
    ].head()
)

print("\nSummary statistics:")
print(
    historical_df[
        [
            "Shots_Per_Match",
            "Shots_On_Target_Per_Match",
            "Fouls_Per_Match",
            "Yellow_Cards_Per_Match",
            "Red_Cards_Per_Match",
            "Shot_Conversion_Percentage",
            "xG_Difference_Per_Match",
            "Points_Per_Match"
        ]
    ].describe()
)

# CURRENT TEAM-SEASON METRICS

current_team_stats["Shots_Per_Match"] = (
    current_team_stats["Shots"] / current_team_stats["Matches_Played"]
)

current_team_stats["Shots_On_Target_Per_Match"] = (
    current_team_stats["Shots_On_Target"] / current_team_stats["Matches_Played"]
)

current_team_stats["Fouls_Per_Match"] = (
    current_team_stats["Fouls"] / current_team_stats["Matches_Played"]
)

current_team_stats["Yellow_Cards_Per_Match"] = (
    current_team_stats["Yellow_Cards"] / current_team_stats["Matches_Played"]
)

current_team_stats["Red_Cards_Per_Match"] = (
    current_team_stats["Red_Cards"] / current_team_stats["Matches_Played"]
)

# DERIVE CURRENT SEASON xG FROM UNDERSTAT SHOT-LEVEL DATA
current_shots = pd.read_csv(
    "data/processed/pl_2026_27_shots_processed.csv"
)
 
understat_team_mapping = {
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Newcastle United": "Newcastle",
    "Nottingham Forest": "Nott'm Forest",
    "Wolverhampton Wanderers": "Wolves"
}
 
current_shots["team"] = current_shots["team"].replace(understat_team_mapping)
 
current_shots["opponent"] = current_shots.apply(
    lambda row: (
        row["a_team"] if row["team_side"] == "home" else row["h_team"]
    ),
    axis=1
)
 
current_shots["opponent"] = current_shots["opponent"].replace(
    understat_team_mapping
)
 
xg_for = (
    current_shots.groupby("team")["xG"].sum().rename("Total_xG_For")
)
 
xg_against = (
    current_shots.groupby("opponent")["xG"].sum().rename("Total_xG_Against")
)
 
current_team_stats = current_team_stats.merge(
    xg_for, left_on="Team", right_index=True, how="left"
)
 
current_team_stats = current_team_stats.merge(
    xg_against, left_on="Team", right_index=True, how="left"
)
 
missing_shot_xg = current_team_stats[
    current_team_stats["Total_xG_For"].isnull()
]["Team"].tolist()
 
if missing_shot_xg:
    print(
        "\nTeams with match results but no shot-level xG data yet "
        "(likely a lag between results and shot-data fetch, or a "
        "team-name mismatch - check first):"
    )
    print(missing_shot_xg)
 
current_team_stats["xG_Per_Match"] = (
    current_team_stats["Total_xG_For"] / current_team_stats["Matches_Played"]
)
 
current_team_stats["xGA_Per_Match"] = (
    current_team_stats["Total_xG_Against"] / current_team_stats["Matches_Played"]
)
 
current_team_stats["xG_Difference_Per_Match"] = (
    current_team_stats["xG_Per_Match"] - current_team_stats["xGA_Per_Match"]
)


# SAFETY NET: a team can have match results but no shot-level xG yet
xg_cols_needing_fallback = [
    "xG_Per_Match",
    "xGA_Per_Match",
    "xG_Difference_Per_Match"
]
 
for col in xg_cols_needing_fallback:
    if current_team_stats[col].isnull().any():
        league_avg_this_season = current_team_stats[col].mean()
        current_team_stats[col] = current_team_stats[col].fillna(
            league_avg_this_season
        )

print("\nCurrent season per-match metrics:")
print(
    current_team_stats[
        [
            "Team",
            "Shots_Per_Match",
            "Shots_On_Target_Per_Match",
            "Fouls_Per_Match",
            "Yellow_Cards_Per_Match",
            "Red_Cards_Per_Match",
            "Shot_Conversion_Percentage",
            "xG_Difference_Per_Match"

        ]
    ]
)

# COMPARE CURRENT TEAMS TO HISTORICAL RANGES

comparison_columns = [
    "Shots_Per_Match",
    "Shots_On_Target_Per_Match",
    "Fouls_Per_Match",
    "Yellow_Cards_Per_Match",
    "Red_Cards_Per_Match",
    "Shot_Conversion_Percentage",
    "xG_Difference_Per_Match"
]

print("\nHistorical ranges:")
print(
    historical_df[comparison_columns]
    .agg(["min", "mean", "max"])
)

print("\nCurrent season ranges:")
print(
    current_team_stats[comparison_columns]
    .agg(["min", "mean", "max"])
)

# TRAIN PER-MATCH PREDICTION MODEL

from sklearn.model_selection import KFold, cross_val_predict
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

features = [
    "Shots_On_Target_Per_Match",
    "Shot_Conversion_Percentage",
    "Fouls_Per_Match",
    "Yellow_Cards_Per_Match",
    "Red_Cards_Per_Match",
    "xG_Difference_Per_Match"
]

target = "Points_Per_Match"

X = historical_df[features]
y = historical_df[target]

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
 
cv_predictions = cross_val_predict(
    LinearRegression(),
    X,
    y,
    cv=cv
)
 
print("\nPoints Per Match Model Performance (5-fold cross-validated):")
print("R-Squared:", r2_score(y, cv_predictions))
print("Mean Absolute Error:", mean_absolute_error(y, cv_predictions))
print(
    "Root Mean Squared Error:",
    np.sqrt(mean_squared_error(y, cv_predictions))
)
 
# FIT THE FINAL MODEL ON ALL HISTORICAL DATA
# Cross-validation above is for evaluating how well this feature set
# predicts unseen data; the model actually used to predict the current
# season should be fit on every available historical row, not held
# back to an 80% split - there's no "test set" to protect once this
# model moves on to predicting a season with no known answer
 
ppm_model = LinearRegression()
ppm_model.fit(X, y)

# EXAMINE MODEL COEFFICIENTS

coefficients = pd.DataFrame({
    "Feature": features,
    "Coefficient": ppm_model.coef_
 })

coefficients = coefficients.sort_values(
    by="Coefficient",
    ascending=False
)

print("\nModel coefficients:")
print(coefficients)

print("\nIntercept:")
print(ppm_model.intercept_)

# Store coefficients keyed by feature name so downstream impact/recommendation calculations always
# match the model actually trained above.
# Avoids coefficients from going stale during the weekly data refresh
model_coeffients = dict(zip(features, ppm_model.coef_))

# CREATE PREDICTIONS FOR THE CURRENT SEASON

current_X = current_team_stats[features]

# Clip predictions to the range that's actually possible in a real
# match: a team can win (3), draw (1), or lose (0) 
current_team_stats["Predicted_Points_Per_Match"] = (
    ppm_model.predict(current_X)
).clip(0, 3)

current_team_stats["Predicted_Season_Points"] = (
    current_team_stats["Predicted_Points_Per_Match"] * 38
)

# Sort teams by projected season points
current_projections = (
    current_team_stats[
        [
            "Team",
            "Points",
            "Matches_Played",
            "Predicted_Points_Per_Match",
            "Predicted_Season_Points"
        ]
    ]
    .sort_values(
        by="Predicted_Season_Points",
        ascending=False
    )
    .reset_index(drop=True)
)

# Add projected league position
current_projections.index = current_projections.index + 1
current_projections.index.name = "Projected_Position"

print("\nCurrent Season Projections:")
print(current_projections)

# RANK TEAMS WITHIN EACH SEASON

historical_rankings = historical_df.copy()

historical_rankings["Position"] = (
    historical_rankings
    .groupby("Season")["Points"]
    .rank(method="first", ascending=False)
)

# Historical qualification threshold
top5_threshold = (
    historical_rankings[
        historical_rankings["Position"] == 5
    ]
    .groupby("Season")["Points"]
    .first()
)

top6_threshold = (
    historical_rankings[
        historical_rankings["Position"] == 6
    ]
    .groupby("Season")["Points"]
    .first()
)

champion_threshold = (
    historical_rankings[
        historical_rankings["Position"] == 1
    ]
    .groupby("Season")["Points"]
    .first()
)

print("\nTop 6 thresholds:")
print(top6_threshold)

print("\nTop 5 thresholds:")
print(top5_threshold)

print("\nChampion points:")
print(champion_threshold)

print("\nAverage thresholds:")

print("Average Top 6 threshold:", top6_threshold.mean())
print("Average Top 5 threshold:", top5_threshold.mean())
print("Average Champion points:", champion_threshold.mean())

# Historical performance targets 
TOP6_TARGET = round(top6_threshold.mean())
TOP5_TARGET = round(top5_threshold.mean())
CHAMPION_TARGET = round(champion_threshold.mean())

print("\nPerformance targets:")
print("Top 6:", TOP6_TARGET)
print("Top 5:", TOP5_TARGET)
print("Champions:", CHAMPION_TARGET)

# Compare projection against targets
current_projections["Gap_to_Top_6"] = (
    TOP6_TARGET -
    current_projections["Predicted_Season_Points"]
)

current_projections["Gap_to_Top_5"] = (
    TOP5_TARGET -
    current_projections["Predicted_Season_Points"]
)

current_projections["Gap_to_Champion"] = (
    CHAMPION_TARGET -
    current_projections["Predicted_Season_Points"]
)

# Teams already projected above a target should have a gap of 0
gap_columns = [
    "Gap_to_Top_6",
    "Gap_to_Top_5",
    "Gap_to_Champion"
]

current_projections[gap_columns] = (
    current_projections[gap_columns]
    .clip(lower=0)
)

print("\nProjections compared with historical targets:")

print(
    current_projections[
        [
            "Team",
            "Predicted_Season_Points",
            "Gap_to_Top_6",
            "Gap_to_Top_5",
            "Gap_to_Champion"
        ]
    ]
)

# CREATE HISTORICAL PERFORMANCE BASELINE FOR EACH TEAM

team_historical_baseline = (
    historical_df
    .groupby("Team")[features]
    .mean()
    .reset_index()
)

print("\nTeam historical performance baseline:")
print(team_historical_baseline)

current_teams = set(current_team_stats["Team"])
historical_teams = set(team_historical_baseline["Team"])

teams_without_history = current_teams - historical_teams

print("\nTeams without historical Premier League data:")
print(teams_without_history)

team_season_counts = (
    historical_df
    .groupby("Team")["Season"]
    .nunique()
    .sort_values()
)

print("\nNumber of historical seasons per team:")
print(team_season_counts)

# MERGE HISTORICAL BEASELINE WITH CURRENT STATISATICS
 
team_season_counts = (
    historical_df
    .groupby("Team")["Season"]
    .nunique()
    .reset_index()
    .rename(columns={"Season": "Historical_Seasons"})
)

team_historical_baseline = (
    team_historical_baseline
    .merge(
        team_season_counts,
        on="Team",
        how="left"
    )
)

print(team_historical_baseline.head())

current_with_baseline = current_team_stats.merge(
    team_historical_baseline,
    on="Team",
    how="left",
    suffixes=("_Current", "_Historical")
)

print("\nCurrent season data with historical baseline:")
print(
    current_with_baseline[
        [
            "Team",
            "Matches_Played",
            "Historical_Seasons"
        ]
        
    ]
)
# Coventry's missing historical baseline (replace with league average)
features = [
    "Shots_On_Target_Per_Match",
    "Shot_Conversion_Percentage",
    "Fouls_Per_Match",
    "Yellow_Cards_Per_Match",
    "Red_Cards_Per_Match",
    "xG_Difference_Per_Match"
]

league_baseline = (
    historical_df[features]
    .mean()
    .to_frame()
    .T
)

print("League historical baseline:")
print(league_baseline)

for feature in features:
    historical_column = feature + "_Historical"

    current_with_baseline[historical_column] = (
        current_with_baseline[historical_column]
        .fillna(league_baseline[feature].iloc[0])
    )

current_with_baseline["Historical_Seasons"] = (
    current_with_baseline["Historical_Seasons"]
    .fillna(0)
)

print("\nMissing values after baseline adjustment:")
print(
    current_with_baseline[
        [feature + "_Historical" for feature in features]
    ].isnull().sum()
)

# COMPARE CURRENT PERFORMANCE WITH  HISTORICAL BASELINE

for feature in features:
    current_columns = feature + "_Current"
    historical_column = feature + "_Historical"
    difference_column = feature + "_Difference"

    current_with_baseline[difference_column] = (
        current_with_baseline[current_columns] -
        current_with_baseline[historical_column]
    )

print("\nCurrent performance compared with historical baseline:")

comparison_columns = [
    "Team",
    "Matches_Played",
    "Historical_Seasons"
    ]

for feature in features:
    comparison_columns.extend([
        feature + "_Current",
        feature + "_Historical",
        feature + "_Difference"

    ])

print(current_with_baseline[comparison_columns])

# MODEL COEFFICIENTS

print("\nCoefficients used for impact calculations:")
print(model_coeffients)

# Calculate impact of current performance differences

for feature in features:
    difference_column = feature + "_Difference"
    impact_columns = feature + "_Points_Per_Match_Impact"

    current_with_baseline[impact_columns] = (
        current_with_baseline[difference_column] * model_coeffients[feature]
    )

print("\nImpact of current performance differences on predicted points per match:")

impact_columns = [
    "Team",
    "Historical_Seasons"
]

for feature in features:
    impact_columns.append(
        feature + "_Points_Per_Match_Impact"
    )

print(current_with_baseline[impact_columns])

# TOTAL PERFORMANCE IMPACT

impact_columns = [
    feature + "_Points_Per_Match_Impact"
    for feature in features
]

current_with_baseline["Total_Performance_Impact"] = (
    current_with_baseline[impact_columns]
    .sum(axis=1)
)

impact_summary = current_with_baseline[
    [
        "Team",
        "Historical_Seasons",
        "Predicted_Points_Per_Match",
        "Total_Performance_Impact"
    ]
].sort_values(
    "Total_Performance_Impact",
    ascending=False
)

print("\nTotal impact of current performance compared with historical baseline:")
print(impact_summary)

# BIGGEST FACTOR/S HELPING AND HURTING EACH TEAM

impact_results = []

for _, row in current_with_baseline.iterrows():
    impacts = {}

    for feature in features:
        impact_columns = feature + "_Points_Per_Match_Impact"
        impacts[feature] = row[impact_columns]

    positive_impacts = {
        feature: impact
        for feature, impact in impacts.items()
        if impact > 0
    }

    negative_impacts = {
        feature: impact
        for feature, impact in impacts.items()
        if impact < 0
    }

    if positive_impacts:
        best_factor = max(
            positive_impacts,
            key=positive_impacts.get
        )
        best_impact = positive_impacts[best_factor]
    else:
        best_factor = "None"
        best_impact = 0

    if negative_impacts:
        worst_factor = min(
            negative_impacts,
            key=negative_impacts.get
        )
        worst_impact = negative_impacts[worst_factor]
    else:
        worst_factor = "None"
        worst_impact = 0

    impact_results.append({
        "Team": row["Team"],
        "Predicted_Points_Per_Match": row["Predicted_Points_Per_Match"],
        "Total_Performance_Impact": row["Total_Performance_Impact"],

        "Biggest_Positive_Factor": best_factor,
        "Positive_Impact": best_impact,

        "Biggest_Negative_Factor": worst_factor,
        "Negative_Impact": worst_impact
    })

team_recommendations = pd.DataFrame(impact_results)

team_recommendations = team_recommendations.sort_values(
    "Predicted_Points_Per_Match",
    ascending=False
)

print("\nTeam performance factors:")
print(team_recommendations)

# RECOMMENDATIONS

recommendation_map = {
    "Shots_On_Target_Per_Match":
        "Improve attacking accuracy and create more shots on target.",

    "Shot_Conversion_Percentage":
        "Improve finishing efficiency and convert a higher proportion of shots into goals.",

    "Fouls_Per_Match":
        "Reduce unnecessary fouls and improve defensive discipline.",

    "Yellow_Cards_Per_Match":
        "Reduce disciplinary issues and avoid unnecessary yellow cards.",

    "Red_Cards_Per_Match":
        "Improve discipline and reduce the risk of red cards.",

    "xG_Difference_Per_Match":
        "Improve the balance between chance creation and chance prevention - either create higher-quality chances or tighten up defensively.",

    "None":
        "Maintain current performance across the modelled metrics."
}

team_recommendations["Recommendation"] = (
    team_recommendations["Biggest_Negative_Factor"]
    .map(recommendation_map)
)

print("\nTeam recommendations:")
print(
    team_recommendations[
        [
            "Team",
            "Predicted_Points_Per_Match",
            "Total_Performance_Impact",
            "Biggest_Negative_Factor",
            "Recommendation"
        ]
    ]
)

def classify_target(row):

    if row["Predicted_Season_Points"] >= 92:
        return "Championship Contender"

    elif row["Predicted_Season_Points"] >= 67:
        return "Top 5 Contender"

    elif row["Predicted_Season_Points"] >= 63:
        return "Top 6 Contender"
    
    else:
        return "Below Historical Qualification Targets"

current_with_baseline["Performance_Target"] = (
    current_with_baseline.apply(classify_target, axis=1)
)

projection_columns = [
     "Team",
     "Predicted_Points_Per_Match",
     "Predicted_Season_Points",
     "Gap_to_Top_6",
     "Gap_to_Top_5",
     "Gap_to_Champion"
]

current_with_baseline = current_with_baseline.merge(
    current_projections[projection_columns],
    on="Team",
    how="left",
    suffixes=("", "_Projection")
)

powerbi_df = current_with_baseline.merge(
    team_recommendations[
        [
            "Team",
            "Biggest_Positive_Factor",
            "Positive_Impact",
            "Biggest_Negative_Factor",
            "Negative_Impact",
            "Recommendation"
        ]
    ],
    on="Team",
    how="left"
)


powerbi_columns = [
    "Team",

    # Current performance
    "Matches_Played",
    "Points",

    # Predictions
    "Predicted_Points_Per_Match",
    "Predicted_Season_Points",
    "Performance_Target",

    # Historical context
    "Historical_Seasons",
    "Total_Performance_Impact",

    # Target gaps
    "Gap_to_Top_6",
    "Gap_to_Top_5",
    "Gap_to_Champion",


    # Current metrics
    "Shots_On_Target_Per_Match_Current",
    "Shot_Conversion_Percentage_Current",
    "Fouls_Per_Match_Current",
    "Yellow_Cards_Per_Match_Current",
    "Red_Cards_Per_Match_Current",
    "xG_Difference_Per_Match_Current",

    # Historical metrics
    "Shots_On_Target_Per_Match_Historical",
    "Shot_Conversion_Percentage_Historical",
    "Fouls_Per_Match_Historical",
    "Yellow_Cards_Per_Match_Historical",
    "Red_Cards_Per_Match_Historical",
    "xG_Difference_Per_Match_Historical",

    # Differences
    "Shots_On_Target_Per_Match_Difference",
    "Shot_Conversion_Percentage_Difference",
    "Fouls_Per_Match_Difference",
    "Yellow_Cards_Per_Match_Difference",
    "Red_Cards_Per_Match_Difference",
    "xG_Difference_Per_Match_Difference",

    # Recommendations
    "Biggest_Positive_Factor",
    "Positive_Impact",
    "Biggest_Negative_Factor",
    "Negative_Impact",
    "Recommendation"
]

powerbi_df = powerbi_df[powerbi_columns]

print(powerbi_df.head())
print(powerbi_df.columns)


# CREATE AND EXPORT POWER BI DATASET

print("\nPower BI Dataset:")
print(powerbi_df.head())

print("\nColumns:")
print(powerbi_df.columns)

powerbi_df.to_csv("data/processed/powerbi_current_season_analysis.csv", index=False)