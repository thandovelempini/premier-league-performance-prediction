import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
XG_DATA_DIR = BASE_DIR / "data" / "raw" / "xG"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

all_files = sorted(XG_DATA_DIR.glob("*.csv"))

dataframes = []

for file in all_files:
    df = pd.read_csv(file, sep=";")

    # Extract season from filename
    season = file.stem.replace("xG", "")
    df["Season"] = season
    dataframes.append(df)

# Combine all seasons
xg_data = pd.concat(dataframes, ignore_index=True)

print(xg_data.head())

print("\nSeasons:")
print(xg_data["Season"].unique())

print("\nShape:")
print(xg_data.shape)

# Format season labels
xg_data["Season"] = (
    "20" + xg_data["Season"].str[:2] + "/" + 
    xg_data["Season"].str[2:]
)

print("\nFormatted Seasons:")
print(xg_data["Season"].unique())

# EXPECTED PERFORMANCE METRICS

# Expected goals created per match
xg_data["xG_Per_Match"] = (
    xg_data["xG"] / xg_data["matches"]
)

# Expected goals conceded per match
xg_data["xGA_Per_Match"] = (
    xg_data["xGA"] / xg_data["matches"]
)

# Expected goal difference
xg_data["xG_Difference"] = (
    xg_data["xG"] - xg_data["xGA"]
)

# Expected goal difference per match
xg_data["xG_Difference_Per_Match"] = (
    xg_data["xG_Per_Match"] - xg_data["xGA_Per_Match"]
)

# Expected goals created per match
xg_data["Goals_vs_xG"] = (
    xg_data["goals"] - xg_data["xG"]
)

# Actual goals conceded compared with expected goals conceded
xg_data["Goals_Conceded_vs_xGA"] = (
    xg_data["ga"] - xg_data["xGA"]
)

# Actual points compared with expected points
xg_data["Points_vs_xPTS"] = (
    xg_data["points"] - xg_data["xPTS"]
)

expected_metrics = [
    "Season",
    "team",
    "points",
    "xPTS",
    "xG_Per_Match",
    "xGA_Per_Match",
    "xG_Difference",
    "Goals_vs_xG",
    "Points_vs_xPTS"
]

print("\nExpected Performance Metrics:")
print(xg_data[expected_metrics].head())

# DATA QUALITY CHECK

print("\nMissing Values:")
print(xg_data.isnull().sum())

# Summary statistics
expected_performance_columns = [
    "xG_Per_Match",
    "xGA_Per_Match",
    "xG_Difference",
    "xG_Difference_Per_Match",
    "Goals_vs_xG",
    "Goals_Conceded_vs_xGA",
    "Points_vs_xPTS"
]

print("\nSummary Statistics:")
print(xg_data[expected_performance_columns].describe())

# CORRELATION ANALYSIS

correlation_columns = [
    "points",
    "xG",
    "xGA",
    "xPTS",
    "xG_Per_Match",
    "xGA_Per_Match",
    "xG_Difference",
    "xG_Difference_Per_Match",
    "Goals_vs_xG",
    "Goals_Conceded_vs_xGA",
    "Points_vs_xPTS"
]

correlation_matrix = xg_data[correlation_columns].corr()

points_correlation = (
    correlation_matrix["points"]
    .drop("points")
    .sort_values(ascending=False)
)

print("\nCorrelation with Premier League Points:")
print(points_correlation)

# EXPECTED PERFORMANCE CORRELATION RANKING

# Historical compeleted seasons
analysis_columns = [
    "xG_Per_Match",
    "xGA_Per_Match",
    "xG_Difference_Per_Match",
    "Goals_vs_xG",
    "Goals_Conceded_vs_xGA"
]

historical_xg_data = xg_data[
    xg_data["Season"] != "2026/27"
].copy()

historical_correlation = (
    historical_xg_data[
        analysis_columns + ["points"]
    ]
    .corr()["points"]
    .drop("points")
    .sort_values(key=abs, ascending=False)
)

print("\nHistorical Correlation Ranking:")
print(historical_correlation)

# Seasons including current 2026/27 

correlation_with_points = (
    xg_data[analysis_columns + ["points"]]
    .corr()["points"]
    .drop("points")
)

correlation_ranking = correlation_with_points.sort_values(
    key=abs,
    ascending=False
)

print("\nCorrelation Ranking (Including 2026/27 Season):")
print(correlation_ranking) 
# Finding: balance between chance creation and chance prevention matters more than attacking or defensive performance alone


# VISUALISATION: 
# HISTORICAL xG DIFFERENCE PER MATCH VS POINTS (2016/17-2025/26)

plt.figure(figsize=(10, 6))

plt.scatter(
    historical_xg_data["xG_Difference_Per_Match"],
    historical_xg_data["points"]
)

slope, intercept = np.polyfit(
    historical_xg_data["xG_Difference_Per_Match"],
    historical_xg_data["points"],
    1
)

trend_line = (
    slope * historical_xg_data["xG_Difference_Per_Match"] + intercept
)

plt.plot(
    historical_xg_data["xG_Difference_Per_Match"],
    trend_line
)

plt.xlabel("xG Difference per Match:")
plt.ylabel("Premier League Points")

plt.title(
    "Relationship Between xG Difference per Match and Premier League Points\n"
    "(2016/17-2025/26)"
)

plt.grid(True, alpha=0.3)
plt.show()
# Finding: xG difference per match has an extremely strong positive correlation with Premier League points
# An incomplete season can distort relationships between cumulative outcomes and performance metrics


# HISTORICAL xG PER MATCH VS POINTS
plt.figure(figsize=(10, 6))

plt.scatter(
    historical_xg_data["xG_Per_Match"],
    historical_xg_data["points"]
)

slope, intercept = np.polyfit(
    historical_xg_data["xG_Per_Match"],
    historical_xg_data["points"],
    1
)

trend_line = (
    slope * historical_xg_data["xG_Per_Match"] + intercept
)

plt.plot(
    historical_xg_data["xG_Per_Match"],
    trend_line
)

plt.xlabel("xG per Match:")
plt.ylabel("Premier League Points")

plt.title(
    "Relationship Between xG per Match and Premier League Points\n"
    "(2016/17-2025/26)"
)

plt.grid(True, alpha=0.3)
plt.show()
# Finding: Teams that create higher-quality chances generally earn more points

# HISTORICAL xGA PER MATCH VS POINTS
plt.figure(figsize=(10, 6))

plt.scatter(
    historical_xg_data["xGA_Per_Match"],
    historical_xg_data["points"]
)

slope, intercept = np.polyfit(
    historical_xg_data["xGA_Per_Match"],
    historical_xg_data["points"],
    1
)

trend_line = (
    slope * historical_xg_data["xGA_Per_Match"] + intercept
)

plt.plot(
    historical_xg_data["xGA_Per_Match"],
    trend_line
)

plt.xlabel("xGA per Match:")
plt.ylabel("Premier League Points")

plt.title(
    "Relationship Between xGA per Match and Premier League Points\n"
    "(2016/17-2025/26)"
)

plt.grid(True, alpha=0.3)
plt.show()
# Finding: Teams that allow fewer high-quality chances generally earn more points


# BIGGEST OVERPERFORMERS AND UNDERPERFORMERS:
# POINTS VS xPTS ANALYSIS

# Teams that earned the most points above expectation
top_points = (
    historical_xg_data[
        ["Season", "team", "points", "xPTS", "Points_vs_xPTS"]
    ]
    .sort_values("Points_vs_xPTS", ascending=False)
    .head(10)
)

print("\nTop 10 Point Overperformers:")
print(top_points)


# Teams that earned the fewest points compared to expectation
bottom_point = (
    historical_xg_data[
        ["Season", "team", "points", "xPTS", "Points_vs_xPTS"]
    ]
    .sort_values("Points_vs_xPTS", ascending=True)
    .head(10)
)

print("\nTop 10 Point Underperformers:")
print(bottom_point)

top_point_overperformers = (
    historical_xg_data
    .sort_values("Points_vs_xPTS", ascending=False)
    .head(10)
)

top_point_underperformers = (
    historical_xg_data
    .sort_values("Points_vs_xPTS", ascending=True)
    .head(10)
)

comparison_data = pd.concat(
    [top_point_overperformers, top_point_underperformers]
).sort_values("Points_vs_xPTS")

plt.figure(figsize=(16,9))

plt.barh(
    comparison_data["team"] + " (" + comparison_data["Season"] + ")",
    comparison_data["Points_vs_xPTS"]
)

plt.xlabel("Actual Points Minus Expected Points (xPTS)")
plt.ylabel("Team and Season")

plt.title(
    "Largest Premier League Point Overperformers and Underperformers\n"
    "(2016/17-2025/26)"
)

plt.axvline(0)
plt.grid(axis="x", alpha=0.3)
plt.subplots_adjust(left=0.25)
plt.show()


# GOALS VS xG ANALYSIS

# Teams that scored the most goals above expectations
top_goals = (
    historical_xg_data[
        ["Season", "team", "goals", "xG", "Goals_vs_xG"]
    ]
    .sort_values("Goals_vs_xG", ascending=False)
    .head(10)
)

print("\nTop 10 Goal Overperformers:")
print(top_goals)

# Teams that scored the fewest goals compared to expectations
bottom_goals = (
    historical_xg_data[
        ["Season", "team", "goals", "xG", "Goals_vs_xG"]
    ]
    .sort_values("Goals_vs_xG", ascending=True)
    .head(10)
)

print("\nTop 10 Goal Underperformers:")
print(bottom_goals)

top_goal_overperformers = (
    historical_xg_data
    .sort_values("Goals_vs_xG", ascending=False)
    .head(10)
)

top_goal_underperformers = (
    historical_xg_data
    .sort_values("Goals_vs_xG", ascending=True)
    .head(10)
)

comparison_data = pd.concat(
    [top_goal_overperformers, top_goal_underperformers]
).sort_values("Goals_vs_xG")

plt.figure(figsize=(16,9))

plt.barh(
    comparison_data["team"] + " (" + comparison_data["Season"] + ")",
    comparison_data["Goals_vs_xG"]
)

plt.xlabel("Actual Goals Minus Expected Goals (xG)")
plt.ylabel("Team and Season")

plt.title(
    "Largest Premier League Goal Overperformers and Underperformers\n"
    "(2016/17-2025/26)"
)

plt.axvline(0)
plt.grid(axis="x", alpha=0.3)
plt.subplots_adjust(left=0.25)
plt.show()

# GOALS CONCEDED VS xGA ANALYSIS

# Teams that CONCEDED the most goals above expectations
top_conceding = (
    historical_xg_data[
        ["Season", "team", "ga", "xGA", "Goals_Conceded_vs_xGA"]
    ]
    .sort_values("Goals_Conceded_vs_xGA", ascending=False)
    .head(10)
)

print("\nTop 10 Teams Conceding More Goals Than Expected:")
print(top_conceding)

# Teams that scored the fewest goals compared to expectations
bottom_conceding = (
    historical_xg_data[
        ["Season", "team", "ga", "xGA", "Goals_Conceded_vs_xGA"]
    ]
    .sort_values("Goals_Conceded_vs_xGA", ascending=True)
    .head(10)
)

print("\nTop 10 Teams Conceding Fewer Goals Than Expected:")
print(bottom_conceding)

top_goal_conceders = (
    historical_xg_data
    .sort_values("Goals_Conceded_vs_xGA", ascending=False)
    .head(10)
)

bottom_goal_conceders = (
    historical_xg_data
    .sort_values("Goals_Conceded_vs_xGA", ascending=True)
    .head(10)
)

comparison_data = pd.concat(
    [top_goal_conceders, bottom_goal_conceders]
).sort_values("Goals_Conceded_vs_xGA")

plt.figure(figsize=(16,9))

plt.barh(
    comparison_data["team"] + " (" + comparison_data["Season"] + ")",
    comparison_data["Goals_Conceded_vs_xGA"]
)

plt.xlabel("Actual Goals Conceded Minus Expected Goals Conceded (xGA)")
plt.ylabel("Team and Season")

plt.title(
    "Largest and Smallest Premier League Goal Conceders\n"
    "(2016/17-2025/26)"
)

plt.axvline(0)
plt.grid(axis="x", alpha=0.3)
plt.subplots_adjust(left=0.25)
plt.show()

# RELATIONSHIP BETWEEN EXPECTED PERFORMANCE AND POINTS

performance_metrics = [
    "xG_Per_Match",
    "xGA_Per_Match",
    "xG_Difference_Per_Match",
    "Goals_vs_xG",
    "Goals_Conceded_vs_xGA",
    "Points_vs_xPTS" 
]

correlations = historical_xg_data[
    performance_metrics + ["points"]
].corr()["points"].drop("points")

correlation_summary = (
    correlations 
    .abs()
    .sort_values(ascending=False)
    .to_frame(name="Absolute_Correlation")
)

correlation_summary["Correlation"] = correlations[
    correlation_summary.index
]

print("Expected Performance Metrics Ranked by Relationship with Points:")
print(correlation_summary)

correlation_plot = correlation_summary.sort_values(
    "Correlation",
    ascending=True
)

plt.figure(figsize=(10, 6))

plt.barh(
    correlation_plot.index,
    correlation_plot["Correlation"]
)

plt.axvline(x=0)

plt.title(
    "Relationship Between Expected Performance Metrics\n"
    "and Premier League Points (2016/17-2025/26)"
)

plt.xlabel("Correlation with Premier League Points")
plt.ylabel("Expected Performance Metric")

plt.subplots_adjust(left=0.23, right=0.95)
plt.show()