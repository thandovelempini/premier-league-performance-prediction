import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

# Pipeline order, respecting actual file dependencies between scripts.

STAGES = [
    ["01_load_and_combine.py", "02_create_team_season_data.py"],

    ["build_historical_fact.py"],

    ["06_fetch_shot_data.py", "07_shot_level_analysis.py"],

    ["04_current_season_analysis.py", "08_xg_model_comparison.py",
     "03_exploratory_analysis.py", "05_expected_performance_analysis.py"],

    ["09_shot_profile_dashboard.py"],

    ["11_fetch_injury_status.py"],

    ["10_build_powerbi_schema.py"],
]


def run_script(script_name):
    script_path = SRC_DIR / script_name
    print(f"\n{'=' * 70}")
    print(f"Running: {script_name}")
    print(f"{'=' * 70}")

    start = time.time()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    elapsed = time.time() - start

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    success = result.returncode == 0
    status = "OK" if success else "FAILED"
    print(f"--- {script_name}: {status} ({elapsed:.1f}s) ---")

    return success, elapsed


def main():
    skip_fetch = "--skip-fetch" in sys.argv

    print(f"Weekly pipeline run started: {datetime.now().isoformat(timespec='seconds')}")
    print(
        "\nReminder: this does not fetch raw match results or the "
        "current-season xG snapshot - update those files manually "
        "before running if they haven't been already this week."
    )

    log = []
    pipeline_start = time.time()

    for stage_num, stage_scripts in enumerate(STAGES, start=1):
        print(f"\n\n### STAGE {stage_num} ###")

        for script_name in stage_scripts:
            if skip_fetch and script_name == "06_fetch_shot_data.py":
                print(f"\nSkipping {script_name} (--skip-fetch passed)")
                continue

            success, elapsed = run_script(script_name)
            log.append((script_name, success, elapsed))

            if not success:
                print(
                    f"\n\nPIPELINE STOPPED: {script_name} failed. "
                    "Fix the error above before re-running - later "
                    "stages depend on this script's output and would "
                    "fail or silently use stale data otherwise."
                )
                print_summary(log, time.time() - pipeline_start)
                sys.exit(1)

    print_summary(log, time.time() - pipeline_start)


def print_summary(log, total_elapsed):
    print(f"\n\n{'=' * 70}")
    print("PIPELINE SUMMARY")
    print(f"{'=' * 70}")

    for script_name, success, elapsed in log:
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {script_name} ({elapsed:.1f}s)")

    print(f"\nTotal time: {total_elapsed:.1f}s")

    if all(success for _, success, _ in log):
        print("\nAll steps completed. Power BI files are ready to refresh:")
        print("  - dim_team.csv")
        print("  - fact_team_season_historical.csv")
        print("  - fact_team_current_season.csv")
        print("  - fact_shot_current_season.csv")
        print("  - fact_team_shot_profile_current_season.csv")
        print("  - fact_team_injury_status.csv")


if __name__ == "__main__":
    main()