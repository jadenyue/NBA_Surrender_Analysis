# NBA surrender analysis


Covers 25 regular seasons, 2000-01 to 2024-25.

## Where the data comes from

Play-by-play is from the `playbyplayv2` endpoint at `stats.nba.com`.
I worked from a GitHub mirror of it, `github.com/sumitrodatta/nba-alt-awards`, which
holds one CSV per season named `1996-97_pbp.csv` through `2024-25_pbp.csv`. 

Team strength and coach records come from Basketball Reference, via the same repo's
season summary tables and the coach pages respectively.

## Running it

The first script needs `repo.zip`, the other two only need the CSVs here.

```
python extract_surrenders.py 2000-01 2001-02 ... 2024-25
python analyse_coaches.py
python coach_vs_roster.py
```

`extract_surrenders.py` writes one file per season into `cb_parts/` and skips
anything already done, so it can be stopped and restarted. Roughly a minute per
season.

`analyse_coaches.py` fits the hazard model and writes `coach_hazard_ratios.csv`.
It produces the band table, the likelihood ratio test, the variance decomposition
and the coach rankings.

`coach_vs_roster.py` produces the peak RCR table, the within-coach roster slope, the between-franchise correlation, the two stability tables, the season trend and the completeness checks.

Needs pandas, numpy and scipy.

## Files

| File | What it holds |
| --- | --- |
| `comeback_rate_all.csv` | 40,325 rows, one per trailing team-game. RCR, deficit, minutes left, whether the coach surrendered, and whether the team won |
| `coach_hazard_ratios.csv` | 123 coaches with hazard ratio, games, surrenders and expected count |
| `coach_team.csv` | Each coach split by franchise |
| `coach_team_season.csv` | Each coach split by franchise and season |
| `log_completeness.csv` | Substitutions logged per team-game, for the data quality checks |
| `05_coach_records.csv` | Which coach was in charge for which stretch of games |
| `11_team_strength.csv` | Season level SRS, margin of victory and net rating |

## Columns in comeback_rate_all.csv

| Column | Meaning |
| --- | --- |
| `game_id` | NBA game identifier |
| `team` | Three letter team code |
| `event` | 1 if the coach surrendered at that point, else 0 |
| `rate` | Required comeback rate. For a surrender this is the rate when the coach surrendered, otherwise the worst rate the team faced |
| `margin` | The deficit at that moment, in points |
| `min_left` | Minutes remaining at that moment |
| `season` | For example 2023-24 |
| `season_end_year` | For example 2024 |
| `won_game` | 1 if the team went on to win |

