import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

historical_df = pd.read_csv(PROCESSED_DIR / "premier_league_team_season.csv")
print("\nUsing existing fact_team_season_historical.csv: {historical_df.shape}")


current_season_src = PROCESSED_DIR / "powerbi_current_season_analysis.csv"
fact_team_current_season_path = (
    PROCESSED_DIR / "fact_team_current_season.csv"
)

current_season_df = pd.read_csv(current_season_src)
current_season_df.to_csv(fact_team_current_season_path, index=False)
print(
    f"Saved {fact_team_current_season_path.name}: "
    f"{current_season_df.shape}"
)


shot_export_src = PROCESSED_DIR / "shot_map_export.csv"
fact_shot_current_season_path = (
    PROCESSED_DIR / "fact_shot_current_season.csv"
)

shot_export_df = pd.read_csv(shot_export_src)
shot_export_df.to_csv(fact_shot_current_season_path, index=False)
print(
    f"Saved {fact_shot_current_season_path.name}: "
    f"{shot_export_df.shape}"
)

shot_profile_src = PROCESSED_DIR / "team_shot_profile.csv"
fact_team_shot_profile_path = (
    PROCESSED_DIR / "fact_team_shot_profile_current_season.csv"
)

shot_profile_df = pd.read_csv(shot_profile_src)
shot_profile_df.to_csv(fact_team_shot_profile_path, index=False)
print(
    f"Saved {fact_team_shot_profile_path.name}: "
    f"{shot_profile_df.shape}"
)

 
injury_summary_src = PROCESSED_DIR / "team_injury_summary.csv"
fact_team_injury_status_path = (
    PROCESSED_DIR / "fact_team_injury_status.csv"
)
 
injury_summary_df = pd.read_csv(injury_summary_src)
injury_summary_df.to_csv(fact_team_injury_status_path, index=False)
print(
    f"Saved {fact_team_injury_status_path.name}: "
    f"{injury_summary_df.shape} "
    f"({injury_summary_df['Snapshot_Date'].nunique()} snapshot date(s))"
)
 

historical_seasons = (
    historical_df
    .groupby("Team")["Season"]
    .nunique()
    .reset_index()
    .rename(columns={"Season": "Historical_Seasons"})
)

all_teams = sorted(
    set(historical_df["Team"])
    | set(current_season_df["Team"])
    | set(shot_export_df["Team"])
    | set(shot_profile_df["Team"])
    | set(injury_summary_df["Team"])
)

dim_team = pd.DataFrame({"Team": all_teams})

dim_team = dim_team.merge(
    historical_seasons,
    on="Team",
    how="left"
)

dim_team["Historical_Seasons"] = (
    dim_team["Historical_Seasons"].fillna(0).astype(int)
)

dim_team["Newly_Promoted"] = dim_team["Historical_Seasons"] == 0

dim_team_path = PROCESSED_DIR / "dim_team.csv"
dim_team.to_csv(dim_team_path, index=False)
print(f"\nSaved {dim_team_path.name}: {dim_team.shape}")
print(dim_team.to_string(index=False))

fact_tables = {
    "fact_team_season_historical": historical_df,
    "fact_team_current_season": current_season_df,
    "fact_shot_current_season": shot_export_df,
    "fact_team_shot_profile_current_season": shot_profile_df,
    "fact_team_injury_status": injury_summary_df
}

dim_team_set = set(dim_team["Team"])

print("\n" + "=" * 60)
print("Schema validation: orphaned Team values per fact table")
print("=" * 60)

any_orphans = False
for name, df in fact_tables.items():
    orphans = set(df["Team"].unique()) - dim_team_set
    if orphans:
        any_orphans = True
        print(f"{name}: {sorted(orphans)}")
    else:
        print(f"{name}: OK (all teams found in dim_team)")

if not any_orphans:
    print("\nAll fact tables join cleanly to dim_team on Team.")
