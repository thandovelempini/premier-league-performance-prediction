import pandas as pd
from pathlib import Path
import html
from adjustText import adjust_text

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = (
    BASE_DIR/ "data" / "raw" / "pl_2026_27_shots.csv"
)

shots = pd.read_csv(DATA_PATH)

for column in ["player", "player_assisted"]:
    if column in shots.columns:
        shots[column] = shots[column].apply(
            lambda name: html.unescape(name) if pd.notna(name) else name
        )

print("\nFirst 5 rows:")
print(shots.head())

print("\nDataset shape:")
print(shots.shape)

print("\nColumns:")
print(shots.columns.tolist())

print("\nData types:")
print(shots.dtypes)

print("\nMissing values:")
print(shots.isnull().sum())

print("\nShot results:")
print(shots["result"].value_counts())

print("\nShot situations:")
print(shots["situation"].value_counts())

print("\nShot types:")
print(shots["shotType"].value_counts())

# CREATE SHOOTING TEAM COLUMNS 

shots["team"] = shots.apply(
    lambda row: (
        row["h_team"]
        if row["team_side"] == "home"
        else row["a_team"]
    ),
    axis=1
)

print("\nFirst 5 shots with shooting team:")
print(
    shots[
        [
            "team",
            "player",
            "minute",
            "result",
            "xG",
            "situation",
            "shotType"
        ]
    ].head()
)

# CREATE ANALYSIS VARIABLES

# Identify goals
shots["is_goal"] = (
    shots["result"] == "Goal"
).astype(int)

# Identify high-quality chances
shots["high_xg_chance"] = (
    shots["xG"] >= 0.20
).astype(int)

# Convert date to datetime
shots["date"] = pd.to_datetime(
    shots["date"]
)

print("\nNew columns created:")
print(
    shots[
        [
            "team",
            "result",
            "xG",
            "is_goal",
            "high_xg_chance"
        ]   
    ].head()
)

PROCESSED_DIR = (
    BASE_DIR / "data" / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_path = (
    PROCESSED_DIR / "pl_2026_27_shots_processed.csv"
)

shots.to_csv(output_path, index=False)

print("\nProcessed dataset saved to:")
print(output_path)

# TEAM SHOOTING ANALYSIS

team_shooting = (
    shots.groupby("team")
    .agg(
        Total_Shots = ("id", "count"),
        Goals = ("is_goal", "sum"),
        Total_xG = ("xG", "sum"),
        Average_xG_Per_Shot = ("xG", "mean"),
        High_xG_Chances = ("high_xg_chance", "sum")
    )
    .reset_index()
)

# Conversion rate
team_shooting["Conversion_Rate"] = (
    team_shooting["Goals"] / team_shooting["Total_Shots"] * 100
)

# Round values
team_shooting["Total_xG"] = (
    team_shooting["Total_xG"].round(2)
)

team_shooting["Average_xG_Per_Shot"] = (
    team_shooting["Average_xG_Per_Shot"].round(3)
)

team_shooting["Conversion_Rate"] = (
    team_shooting["Conversion_Rate"].round(2)
)

# Sort by total xG
team_shooting = (
    team_shooting
    .sort_values(
        "Total_xG",
        ascending=False
    )
    .reset_index(drop=True)
)

print("\n" + "=" * 60)
print("Team Shooting Profile")
print("=" * 60)

print(team_shooting.to_string(index=False))

# GOALS VS EXPECTED GOALS

team_shooting["Goals_vs_xG"] = (
    team_shooting["Goals"] - team_shooting["Total_xG"]
).round(2)

# Sort from biggest overperformer
goals_vs_xg = (
    team_shooting[
        [
            "team",
            "Goals",
            "Total_xG",
            "Goals_vs_xG",
            "Conversion_Rate"
        ]
    ]
    .sort_values(
        "Goals_vs_xG",
        ascending=False
    )
    .reset_index(drop=True)
)

print("\n" + "=" * 60)
print("Goals vs Expected Goals")
print("=" * 60)

print(goals_vs_xg.to_string(index=False))

# LEAGUE GOALS VS TOTAL xG CHECK

total_goals = shots["is_goal"].sum()

total_xg = shots["xG"].sum()

difference = total_goals - total_xg

print("\n" + "=" * 60)
print("League Goals vs Expected Goals")
print("=" * 60)

print(f"Total Goals: {total_goals}")
print(f"Total xG: {total_xg:.2f}")
print(f"Goals vs xG: {difference:.2f}")

# Check distribution of goals
print("\nGoal-related results:")
print(
    shots[
        shots["result"].isin(
            ["Goal", "OwnGoal"]
        )
    ]["result"].value_counts()
)

# xG BY SHOT RESULT

xg_by_result = (
    shots
    .groupby("result")
    .agg(
         Shots = ("id", "count"),
         Total_xG = ("xG", "sum"),
         Average_xG = ("xG", "mean"),
                
    )
    .round(3)
    .sort_values("Total_xG", ascending=False)
)

print("\n" + "=" * 60)
print("xG By Shot Result")
print("=" * 60)

print(xg_by_result)

# CHECK FOR DUPLICATE SHOT IDs

duplicate_shots = shots["id"].duplicated().sum()

print("\nDuplicate shot IDs:")
print(duplicate_shots)

print("\nUnique shot IDs:")
print(shots["id"].nunique())

print("\nTotal rows:")
print(len(shots))

print("\nSeasons in shot dataset:")
print(shots["season"].value_counts())

# COMPARE SHOT DATA WITH LEAGUE DATA

CURRENT_SEASON_MATCHES_PATH = (
    BASE_DIR / "data" / "raw" / "season-data" / "season-2627.csv"
)

current_matches = pd.read_csv(CURRENT_SEASON_MATCHES_PATH)

home_stats = pd.DataFrame({
    "Team": current_matches["HomeTeam"],
    "Matches_Played": 1,
    "Points": current_matches["FTR"].map({"H": 3, "D": 1, "A": 0}),
    "Goals_Scored": current_matches["FTHG"],
    "Goals_Conceded": current_matches["FTAG"]
})

away_stats = pd.DataFrame({
    "Team": current_matches["AwayTeam"],
    "Matches_Played": 1,
    "Points": current_matches["FTR"].map({"H": 0, "D": 1, "A": 3}),
    "Goals_Scored": current_matches["FTAG"],
    "Goals_Conceded": current_matches["FTHG"]
})

league_current = (
    pd.concat([home_stats, away_stats], ignore_index=True)
    .groupby("Team", as_index=False)
    .sum(numeric_only=True)
)

print("\n2026/27 League Data (from current-season match results):")
print(
    league_current[
        [
            "Team",
            "Matches_Played",
            "Goals_Scored",
            "Goals_Conceded",
            "Points"
        ]
    ].to_string(index=False)
)

# Compare official goals with shot data
shot_goal_totals = (
    shots
    .groupby("team")
    .agg(
        Shot_Data_Goals=("is_goal", "sum"),
        Shot_Data_xG=("xG", "sum")
    )
    .reset_index()
)

comparison = league_current.merge(
    shot_goal_totals,
    left_on="Team",
    right_on="team",
    how="outer"
)

comparison = comparison[
    [
        "Team",
        "Goals_Scored",
        "Shot_Data_Goals",
        "Shot_Data_xG"
    ]
]

print("\n" + "=" * 60)
print("Official Goals vs Shot Data")
print("=" * 60)

print(comparison.to_string(index=False))

# STANDARDISE TEAM NAMES

team_name_mapping = {
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Newcastle": "Newcastle United",
    "Nott'm Forest": "Nottingham Forest",
    "Wolves": "Wolverhampton Wanderers"
}

league_current["Team_Standardised"] = (
    league_current["Team"]
    .replace(team_name_mapping)
)

# MERGE OFFICIAL GOALS WITH SHOTS xG

comparison = league_current.merge(
    shot_goal_totals,
    left_on="Team_Standardised",
    right_on="team",
    how="left"
)

comparison = comparison[[
        "Team_Standardised",
        "Goals_Scored",
        "Shot_Data_Goals",
        "Shot_Data_xG"
    ]
]

comparison.columns = [
    "Team",
    "Official_Goals",
    "Shot_Data_Goals",
    "Total_xG"
]

print("\n" + "=" * 70)
print("Official Goals vs Shot-Level xG")
print("=" * 70)

print(comparison.to_string(index=False))

# OFFICIAL GOALS VS EXPECTED GOALS 

comparison["Goals_vs_xG"] = (
    comparison["Official_Goals"] - comparison["Total_xG"]
).round(2)

comparison = comparison.sort_values(
    "Goals_vs_xG",
    ascending=False
)

print("\n" + "=" * 70)
print("Official Goals vs Expected Goals")
print("=" * 70)

print(
    comparison[[
            "Team",
            "Official_Goals",
            "Total_xG",
            "Goals_vs_xG"
        ]
    ].to_string(index=False)
)

# Goals vs Expected Goals chart
import matplotlib.pyplot as plt

goals_xg_chart = comparison.sort_values(
    "Goals_vs_xG",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    goals_xg_chart["Team"],
    goals_xg_chart["Goals_vs_xG"]
)

plt.axvline(x=0, linewidth=1)

plt.xlabel("Official Goals Minus Expected Goals (xG)")
plt.ylabel("Team")

plt.title(
    "Premier League Teams: Actual Goals vs Expected Goals\n"
    "(2026/27 Season)"
)

plt.tight_layout()
plt.show()

# RELATIONSHIP BETWEEN GOAL CONVERSION RATE AND PL POINTS

# Merge conversion rate with official league points
conversion_analysis = league_current.merge(
    team_shooting[
        ["team", "Conversion_Rate", "Total_Shots", "Goals", "Total_xG"]
    ],
    left_on="Team_Standardised",
    right_on="team",
    how="inner"
)

conversion_analysis = conversion_analysis[
    ["Team_Standardised", "Points", "Conversion_Rate", "Total_Shots", "Goals", "Total_xG"]
]

conversion_analysis = conversion_analysis.rename(
    columns={"Team_Standardised": "Team"}
)

print("\n" + "=" * 70)
print("Conversion Rate vs Premier League Points")
print("=" * 70)

print(
    conversion_analysis
    .sort_values("Points", ascending=False)
    .to_string(index=False)
)

# Correlation
correlation = conversion_analysis[
    ["Conversion_Rate", "Points"]
].corr().iloc[0, 1]

print(f"\nCorrelation between Conversion Rate and Points: {correlation:.3f}")

# Scatter plot

plt.figure(figsize=(10, 7))

plt.scatter(
    conversion_analysis["Conversion_Rate"],
    conversion_analysis["Points"],
    s=100,
    alpha=0.7
)

labels = [
    plt.text(
        row["Conversion_Rate"],
        row["Points"],
        row["Team"],
        fontsize=8
    )
    for _, row in conversion_analysis.iterrows()
]

adjust_text(
    labels,
    arrowprops=dict(arrowstyle="-", color="grey", lw=0.5)
)

plt.xlabel("Goal Conversion Rate (%)")
plt.ylabel("Premier League Points")

plt.title(
    "Relationship Between Goal Conversion Rate and Premier League Points\n"
    "(2026/27 Season)"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
# Finding: Teams with higher goal conversion generally tend to earn more points
# but conversion rate alone does not strongly explain Premier League success