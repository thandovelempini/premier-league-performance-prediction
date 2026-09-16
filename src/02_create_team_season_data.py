import pandas as pd

premier_league = pd.read_csv("data/processed/premier_league_matches.csv")

# TRANSFORM EACH ROW TO REPRESENT ONE TEAM IN ONE SEASON

# Create home team statistics
home_data = premier_league[
    [
        "Season",
        "HomeTeam",
        "FTHG",
        "FTAG",
        "HS",
        "HST",
        "HF",
        "HC",
        "HY",
        "HR",
        "FTR"
    ]
].copy()

# Rename columns from the home team's perspective 
home_data = home_data.rename(columns={
    "HomeTeam": "Team",
    "FTHG": "Goals_Scored",
    "FTAG": "Goals_Conceded",
    "HS": "Shots",
    "HST": "Shots_On_Target",
    "HF": "Fouls",
    "HC": "Corners",
    "HY": "Yellow_Cards",
    "HR": "Red_Cards"
})

# Create match outcome varibales for home teams
home_data["Wins"] = (home_data["FTR"] == "H").astype(int)
home_data["Draws"] = (home_data["FTR"] == "D").astype(int)
home_data["Losses"] = (home_data["FTR"] == "A").astype(int)

# Create away team statistics 
away_data = premier_league[
    [
        "Season",
        "AwayTeam",
        "FTAG",
        "FTHG",
        "AS",
        "AST",
        "AF",
        "AC",
        "AY",
        "AR",
        "FTR"
    ]
].copy()

# Rename columns from the away team's perspective
away_data = away_data.rename(columns={
    "AwayTeam": "Team",
    "FTAG": "Goals_Scored",
    "FTHG": "Goals_Conceded",
    "AS": "Shots",
    "AST": "Shots_On_Target",
    "AF": "Fouls",
    "AC": "Corners",
    "AY": "Yellow_Cards",
    "AR": "Red_Cards"
})

# Create match outcome varibales for away teams
away_data["Wins"] = (away_data["FTR"] == "A").astype(int)
away_data["Draws"] = (away_data["FTR"] == "D").astype(int)
away_data["Losses"] = (away_data["FTR"] == "H").astype(int)

# Remove the result column, no longer needed
home_data = home_data.drop(columns="FTR")
away_data = away_data.drop(columns="FTR")

# Combine home and away performances
team_matches = pd.concat(
    [home_data, away_data],
    ignore_index=True
)

# Aggregate match statistics into team-season statistics
team_season = team_matches.groupby(
    ["Season", "Team"],
    as_index=False
).sum()

# Create additional variables 
team_season["Matches_Played"] = (
    team_season["Wins"] +
    team_season["Draws"] +
    team_season["Losses"]
)

team_season["Points"] = (
    team_season["Wins"] * 3 +
    team_season["Draws"] 
)

team_season["Goal_Difference"] = (
    team_season["Goals_Scored"] -
    team_season["Goals_Conceded"]
)

# Reorder the columns
team_season = team_season[
    [
        "Season",
        "Team",
        "Matches_Played",
        "Wins",
        "Draws",
        "Losses",
        "Points",
        "Goals_Scored",
        "Goals_Conceded",
        "Goal_Difference",
        "Shots",
        "Shots_On_Target",
        "Fouls",
        "Corners",
        "Yellow_Cards",
        "Red_Cards"
    ]
]

# Sort the dataset
team_season = team_season.sort_values(
    ["Season", "Points"],
    ascending=[True, False]
)

team_season.to_csv("data/processed/premier_league_team_season.csv", index=False)

print(team_season.head())
print("\nDataset shape:", team_season.shape)
print("\nTeams per season:")
print(team_season.groupby("Season")["Team"].count())

# VALIDATION CHECKS

# Check that every team played 38 matches
print("\nTeams that did not play 38 matches:")
print(
    team_season[
        team_season["Matches_Played"] != 38
    ]
)

# Check that Wins + Draws + Losses = 38
print("\nInvalid match outvomr totals:")
print(
    team_season[
        (
            team_season["Wins"] +
            team_season["Draws"] +
            team_season["Losses"]
        ) != team_season["Matches_Played"]
    ]
)

# Check that Points = 3 * Wins + Draws
print("\nInvalid points calculation:")
print(
    team_season[
        team_season["Points"] !=
        team_season["Wins"] * 3 +
        team_season["Draws"]
    ]
)

# Check for missing values
print("\nMissing values:")
print(team_season.isnull().sum())

# Summary of statistics
print("\nSummary statistics:")
print(team_season.describe())
