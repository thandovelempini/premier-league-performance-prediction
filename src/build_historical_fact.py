import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Builds fact_team_season_historical.csv: team-season stats (2016/17-2025/26) 
# merged with historical xG, plus the per-match features the model needs

historical_df = pd.read_csv(PROCESSED_DIR / "premier_league_team_season.csv")

XG_DATA_DIR = RAW_DIR / "xG"
xg_files = sorted(XG_DATA_DIR.glob("*.csv"))

xg_dataframes = []
for file in xg_files:
    df = pd.read_csv(file, sep=";")
    season = file.stem.replace("xG", "")
    df["Season"] = "20" + season[:2] + "/" + season[2:]
    xg_dataframes.append(df)

xg_data = pd.concat(xg_dataframes, ignore_index=True)

xg_name_mapping = {
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Newcastle United": "Newcastle",
    "Nottingham Forest": "Nott'm Forest",
    "West Bromwich Albion": "West Brom",
    "Wolverhampton Wanderers": "Wolves"
}

xg_data["Team"] = xg_data["team"].replace(xg_name_mapping)

known_teams = set(historical_df["Team"].unique())
unmatched_teams = sorted(set(xg_data["Team"].unique()) - known_teams)

if unmatched_teams:
    print(
        "\nExcluding xG rows with no matching historical season "
        "(expected for newly promoted teams, not a data issue):"
    )
    print(unmatched_teams)

xg_data = xg_data[xg_data["Team"].isin(known_teams)].copy()

xg_data["xG_Per_Match"] = xg_data["xG"] / xg_data["matches"]
xg_data["xGA_Per_Match"] = xg_data["xGA"] / xg_data["matches"]
xg_data["xG_Difference_Per_Match"] = (
    xg_data["xG_Per_Match"] - xg_data["xGA_Per_Match"]
)

historical_df = historical_df.merge(
    xg_data[
        ["Season", "Team", "xG_Per_Match", "xGA_Per_Match", "xG_Difference_Per_Match"]
    ],
    on=["Season", "Team"],
    how="left"
)

historical_df["Shots_Per_Match"] = (
    historical_df["Shots"] / historical_df["Matches_Played"]
)
historical_df["Shots_On_Target_Per_Match"] = (
    historical_df["Shots_On_Target"] / historical_df["Matches_Played"]
)
historical_df["Fouls_Per_Match"] = (
    historical_df["Fouls"] / historical_df["Matches_Played"]
)
historical_df["Yellow_Cards_Per_Match"] = (
    historical_df["Yellow_Cards"] / historical_df["Matches_Played"]
)
historical_df["Red_Cards_Per_Match"] = (
    historical_df["Red_Cards"] / historical_df["Matches_Played"]
)
historical_df["Shot_Conversion_Percentage"] = (
    historical_df["Goals_Scored"] / historical_df["Shots"]
) * 100
historical_df["Points_Per_Match"] = (
    historical_df["Points"] / historical_df["Matches_Played"]
)

historical_df = historical_df.dropna(
    subset=["xG_Difference_Per_Match"]
).reset_index(drop=True)

output_path = PROCESSED_DIR / "fact_team_season_historical.csv"
historical_df.to_csv(output_path, index=False)

print(f"\nSaved {output_path.name}: {historical_df.shape}")
print(historical_df.head())