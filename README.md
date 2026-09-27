# Futdentity

**Find statistically similar football players across Europe's top leagues, one aspect of their game at a time.**

Futdentity is a solo football analytics project that uses standardized statistics and Euclidean distance to explore player similarity. Its interactive Python CLI lets you search for a player, choose an aspect of their game, and inspect the closest statistical matches from the 2024–25 season.

**Current stage:** working V1 CLI, with the original exploration retained in a Jupyter notebook. V1 is a similarity baseline; the recommendations have not yet been systematically evaluated for football relevance.

## Features

- Menu-driven player search and an explanation of the method.
- Case- and accent-insensitive exact-name matching: `Kylian Mbappe` matches `Kylian Mbappé`.
- Squad selection when a name appears in multiple records.
- Individual category browsing or all applicable categories at once.
- Up to five matches per category, showing squad, position, minutes, and distance.
- Separate goalkeeper and outfield candidate pools, with a 900-minute minimum for candidates.
- Explicit exclusion of the selected record and non-finite distances.
- Screen clearing between views, input retries, and navigation back to the main menu.

## Getting started

### Requirements

- Python **3.10 or newer**.
- `pandas`, `numpy`, and `scikit-learn` for the CLI.
- A local copy of the expected player CSV. You may find it at Kaggle (https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025/data)
- An interactive terminal. The interface uses the system's `clear` command on macOS/Linux and `cls` on Windows.

From the project root, create an environment and install the CLI dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pandas numpy scikit-learn
```

On Windows PowerShell, use `python` in place of `python3` and activate with `.venv\Scripts\Activate.ps1`.

Run the CLI **from the project root**:

```bash
python -m futdentity.cli
```

Running the file directly with `python futdentity/cli.py` can cause package-import errors. Dependency versions are not pinned yet.

### Search flow

1. Choose **Search for similar players** from the main menu.
2. Enter a full player name, such as `Lamine Yamal`, `Kylian Mbappe`, or `Thibaut Courtois`.
3. If multiple records match, choose the squad record you want to compare.
4. Select a category or **View all categories**.
5. Inspect the results, then press Enter to browse another category.

Use `0` to go back or exit, according to the current menu. Leave the player name blank to return to the main menu. Names must otherwise match exactly after normalization; partial-name and fuzzy searches are not implemented. `Ctrl+C` exits the application.

Example output for **Lamine Yamal → Shooting** with the current local dataset:

```text
Most similar | Shooting
--------------------------------------------------------------------

  1. Bradley Barcola
     Paris S-G | FW | 2,181 min | Distance 5.149

  2. Michael Olise
     Bayern Munich | FW,MF | 2,334 min | Distance 6.225
```

## How similarity works

### Feature preparation

The CSV contains statistics merged across several tables. A column-name rule removes selected redundant columns, and numeric columns are organized into football categories. V1 excludes features tagged as efficiency, percentage, ratio, or conditional, and excludes the entire substitution-context group. Some per-90 rates remain alongside season totals.

### Scaling and distance

For each category, `StandardScaler` standardizes every feature using its mean and standard deviation across the dataset. Each player then becomes a vector of standardized values. Similarity is measured with Euclidean distance:

```text
distance(player, target) = sqrt(sum((player_feature - target_feature)²))
```

Candidates are ranked from smallest to largest distance within each category. **Lower distance means closer statistics.** Distance is not a percentage, probability, or rating of player quality. Categories have different features and dimensions, so their distances should not be compared directly. There is no combined overall similarity score.

### Candidate rules

- Candidates must have at least **900 minutes** in their record.
- Goalkeepers are matched with goalkeepers; outfield players with outfield players. Outfield candidates are not restricted to the same position.
- The selected row is excluded explicitly, including when another row also has zero distance.
- Non-finite distances are excluded. Searches can return fewer than five matches, or no matches.
- A target below 900 minutes can still be searched, with a limited-minutes notice.
- Only the selected record is excluded. Another squad record for the same player may still appear as a candidate.

Scaling is fitted across the full dataset before candidate filtering. The minimum-minutes rule limits who can be recommended; it does not change the scaling population.

## Categories

| Outfield categories | Goalkeeper categories |
| --- | --- |
| Playing time | Team results |
| Shooting | Goalkeeping |
| Passing | Advanced goalkeeping |
| Chance creation | |
| Defense | |
| Possession & carrying | |
| Fouls, recoveries & aerials | |

The exact columns and V1 exclusion rules are defined in [`futdentity/features.py`](futdentity/features.py).

## Data

The current local dataset covers the **2024–25 Premier League, La Liga, Bundesliga, Serie A, and Ligue 1** seasons. It has 2,854 rows, 267 source columns, and 2,702 distinct player-name strings. Rows represent player/squad records, so a name may appear more than once.

**The CSV is not tracked in Git.** A fresh clone needs the expected file placed at:

```text
data/playerdata_2425.csv
```

The loader currently uses this fixed filename. An arbitrary football CSV is unlikely to have the required schema. The dataset's source, collection process, and redistribution terms still need to be documented; a public download or reproducible collection procedure is not provided yet.

## Project structure

```text
Futdentity/
├── data/
│   └── playerdata_2425.csv   # Local input; excluded from Git
├── notebooks/
│   └── main.ipynb           # Exploration and comparison heatmaps
└── futdentity/
    ├── __init__.py
    ├── cli.py              # Menus, input, search orchestration, and display
    ├── data.py             # CSV loading and column preparation
    ├── features.py         # Feature definitions and V1 exclusions
    └── similarity.py       # Scaling, distances, ranking, and name normalization
```

### Explore the notebook

With the virtual environment active, install the additional notebook dependencies and launch from `notebooks/`:

```bash
python -m pip install matplotlib seaborn notebook
cd notebooks
jupyter notebook main.ipynb
```

Run the cells from top to bottom. The notebook reads `../data/playerdata_2425.csv`, so its working directory should be `notebooks/`. The CLI is the primary interactive interface; notebook settings and saved outputs may differ from the current CLI.

## V1 limitations and next steps

- **Playing time affects rankings.** Most features are season totals. Standardization does not remove exposure to minutes played, and low-minute targets can be difficult to compare with higher-minute candidates.
- **Related features can receive extra influence.** Correlated statistics are separate dimensions in the distance calculation. Feature weighting and selection have not been evaluated systematically.
- **Context is only partly represented.** Team tactics, league strength, and detailed positional roles are not explicitly adjusted for.
- **Missing values are filtered, not modeled.** Removing invalid distances prevents misleading rankings but does not resolve why a statistic is missing.
- **Evaluation is still ahead.** Next steps include documenting data provenance, pinning dependencies, reviewing matches across positions, and comparing V1 with a per-90 baseline.

The aim is to build an explainable, reproducible player-similarity tool and measure how its recommendations improve as the method develops.
