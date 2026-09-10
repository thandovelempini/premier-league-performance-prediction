import pandas as pd

files = {
    "data/raw/season-data/season-1617.csv": "2016/17",
    "data/raw/season-data/season-1718.csv": "2017/18",
    "data/raw/season-data/season-1819.csv": "2018/19",
    "data/raw/season-data/season-1920.csv": "2019/20",
    "data/raw/season-data/season-2021.csv": "2020/21",
    "data/raw/season-data/season-2122.csv": "2021/22",
    "data/raw/season-data/season-2223.csv": "2022/23",
    "data/raw/season-data/season-2324.csv": "2023/24",
    "data/raw/season-data/season-2425.csv": "2024/25",
    "data/raw/season-data/season-2526.csv": "2025/26"
}

dataframes = []

for file, season in files.items():
    df = pd.read_csv(file)
    df["Season"] = season
    dataframes.append(df)

premier_league = pd.concat(
    dataframes,
    ignore_index=True
)

print(premier_league.shape)
print(premier_league["Season"].value_counts())

print(premier_league.info())
print(premier_league.head())

# Check for missing values
missing_values = premier_league.isnull().sum()
print("\nMissing values:")
print(missing_values[missing_values > 0])

# Check for duplicate rows
duplicates = premier_league.duplicated().sum()
print("\nNumber of duplicate rows:", duplicates)

# Check the number of teams per season
teams_per_season = pd.concat([
    premier_league.groupby("Season")["HomeTeam"].nunique(),
    premier_league.groupby("Season")["AwayTeam"].nunique()
], axis=1)

teams_per_season.columns = ["Home Teams", "Away Teams"]

print("\nTeams per season:")
print(teams_per_season)

# Get all unique team names
teams = sorted(
    set(premier_league["HomeTeam"].unique())
    | set(premier_league["AwayTeam"].unique())
)

print("\nUnique teams:")
print(teams)

premier_league.to_csv("data/processed/premier_league_matches.csv", index=False)
