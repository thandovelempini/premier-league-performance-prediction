import pandas as pd
import requests
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Fetches live player availability from the official Fantasy Premier
# League API (fantasy.premierleague.com) 

FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

response = requests.get(FPL_API_URL, timeout=30)
response.raise_for_status()
data = response.json()

teams_df = pd.DataFrame(data["teams"])[["id", "name"]]
players_df = pd.DataFrame(data["elements"])

print("\nFPL team names:")
print(sorted(teams_df["name"].unique()))

# Map FPL's team names onto this project's match-data naming convention
fpl_team_mapping = {
    "Man Utd": "Man United",
    "Spurs": "Tottenham",
    "Nott'm Forest": "Nott'm Forest",
    "Coventry City": "Coventry",
    "Hull City": "Hull",
    "Ipswich Town": "Ipswich"
}

teams_df["Team"] = teams_df["name"].replace(fpl_team_mapping)

players_df = players_df.merge(
    teams_df[["id", "Team"]],
    left_on="team",
    right_on="id",
    how="left",
    suffixes=("", "_team")
)

players_df["Player"] = (
    players_df["first_name"] + " " + players_df["second_name"]
)

SNAPSHOT_DATE = date.today().isoformat()
players_df["Snapshot_Date"] = SNAPSHOT_DATE

# status codes: a = available, d = doubtful, i = injured,
# s = suspended, u = unavailable/left club, n = not available (loan)
players_df["Available"] = players_df["status"] == "a"

# A rough "key player" proxy: has played meaningful minutes this season
# No official "first-team" flag exists in this data, so this
# is a judgement call, not a precise cutoff - 450 minutes is roughly 5 full matches

max_minutes_so_far = players_df["minutes"].max()
KEY_PLAYER_MINUTES_FRACTION = 0.5
key_player_threshold = max_minutes_so_far * KEY_PLAYER_MINUTES_FRACTION

players_df["Is_Key_Player"] = (
    players_df["minutes"] >= key_player_threshold
)

player_status_columns = [
    "Snapshot_Date",
    "Team",
    "Player",
    "status",
    "chance_of_playing_next_round",
    "news",
    "minutes",
    "now_cost",
    "Is_Key_Player"
]

player_status = players_df[player_status_columns].rename(columns={
    "status": "Status",
    "chance_of_playing_next_round": "Chance_Of_Playing_Next_Round",
    "news": "News",
    "minutes": "Minutes_This_Season",
    "now_cost": "Now_Cost"
})

# VALIDATE TEAM NAMES

print("\nUnmapped FPL team names:")

if (PROCESSED_DIR / "dim_team.csv").exists():
    dim_team = pd.read_csv(PROCESSED_DIR / "dim_team.csv")
    known_teams = set(dim_team["Team"])
    unmapped = sorted(set(player_status["Team"].dropna().unique()) - known_teams)
    if unmapped:
        print(unmapped)
    else:
        print("None - all FPL teams match dim_team.csv")
else:
    print("dim_team.csv not found yet - skipping cross-check")

# APPEND TO THE HISTORICAL LOG 

player_status_path = PROCESSED_DIR / "injury_status_players.csv"

if player_status_path.exists():
    existing = pd.read_csv(player_status_path)
    existing = existing[existing["Snapshot_Date"] != SNAPSHOT_DATE]
    player_status = pd.concat([existing, player_status], ignore_index=True)

player_status.to_csv(player_status_path, index=False)
print(f"\nSaved {player_status_path.name}: {player_status.shape}")

# TEAM-LEVEL ROLLUP

team_summary = (
    player_status[~player_status["Status"].eq("a") & (player_status["Snapshot_Date"] == SNAPSHOT_DATE)]
    .groupby("Team")
    .agg(
        Total_Unavailable_Players=("Player", "count"),
        Key_Players_Unavailable=("Is_Key_Player", "sum"),
        Total_Missing_Value=("Now_Cost", "sum")
    )
    .reset_index()
)

team_summary["Snapshot_Date"] = SNAPSHOT_DATE

# Ensure every team appears, even ones with zero unavailable players
all_teams = pd.DataFrame({"Team": sorted(player_status["Team"].dropna().unique())})
team_summary = all_teams.merge(team_summary, on="Team", how="left")
team_summary["Snapshot_Date"] = SNAPSHOT_DATE
team_summary[["Total_Unavailable_Players", "Key_Players_Unavailable", "Total_Missing_Value"]] = (
    team_summary[["Total_Unavailable_Players", "Key_Players_Unavailable", "Total_Missing_Value"]]
    .fillna(0)
)

print("\nTeam injury/availability summary:")
print(team_summary.sort_values("Key_Players_Unavailable", ascending=False).to_string(index=False))

team_summary_path = PROCESSED_DIR / "team_injury_summary.csv"

if team_summary_path.exists():
    existing_summary = pd.read_csv(team_summary_path)
    existing_summary = existing_summary[existing_summary["Snapshot_Date"] != SNAPSHOT_DATE]
    team_summary = pd.concat([existing_summary, team_summary], ignore_index=True)

team_summary.to_csv(team_summary_path, index=False)
print(f"\nSaved {team_summary_path.name}: {team_summary.shape}")