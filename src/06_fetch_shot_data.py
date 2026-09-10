import pandas as pd
from pathlib import Path
from understatapi import UnderstatClient

SEASON = "2026"
LEAGUE = "EPL"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

DATA_DIR.mkdir(parents=True, exist_ok=True)

with UnderstatClient() as understat:
    print(f"Fetching {LEAGUE} {SEASON}/27 match data...")

    matches = understat.league(
        league=LEAGUE
    ).get_match_data(
        season=SEASON
    )

    print(f"Matches found: {len(matches)}")

    all_shots = []
    for i, match in enumerate(matches, start=1):
        match_id = str(match["id"])

        print(
            f"Fetching shots for match {i}/{len(matches)} "
            f"(Match ID: {match_id})"
        )

        try:
            shots = understat.match(
                match=match_id
            ).get_shot_data()

            for side in ["h", "a"]:

                for shot in shots.get(side, []):
                    shot["match_id"] = match_id
                    shot["team_side"] = (
                        "home"
                        if side == "h"
                        else "away"
                    )

                    all_shots.append(shot )
        except Exception as e:
            print(f"Could not fetch match {match_id}: {e}")

shots_df = pd.DataFrame(all_shots)

print("\nShot dataset created.")

print("\nShape:")
print(shots_df.shape)

print("\nColumns:")
print(shots_df.columns.tolist())

output_path = DATA_DIR / "pl_2026_27_shots.csv"

shots_df.to_csv(output_path, index=False)

print(f"\nSaved to: {output_path}")