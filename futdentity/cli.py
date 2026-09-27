import pandas as pd
import numpy as np
from futdentity.data import read_data, del_dupe_tokens, get_quantitative
from futdentity.features import get_feature_groups
from futdentity.similarity import scale, get_dist, rank_candidates, normalize_name

MIN_MINUTES = 900
GK_GROUPS = {"team_results", "goalkeeping", "goalkeeping_advanced"}

def select_player(matches:pd.DataFrame) -> int:
    detail_cols = [col for col in ["Squad", "Comp", "Pos"] if col in matches.columns]
    options = matches[["Player", *detail_cols]].reset_index(drop=True)

    print("Multiple players found:")
    for number, (_, player) in enumerate(options.iterrows(), start=1):
        details = ", ".join(f'{col}: {player[col]}' for col in detail_cols)
        print(f'{number}. {player['Player']} ({details})')

    while True:
        choice = input(f'Select the player number (1-{len(matches)}): ').strip()
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches.index[int(choice) - 1]
        print(f"Please enter a number from 1 to {len(matches)}.")

def get_target_idx(name=str, data=pd.DataFrame) -> int:
    matches = data[data["Player"].map(normalize_name) == normalize_name(name)]
    if matches.empty:
        raise ValueError(f"No player found named {name}")
    if len(matches) > 1:
        return select_player(matches)
    return matches.index[0]

def filter_pos(target_is_gk: bool, scaled: dict, data: pd.DataFrame) -> tuple:
    if target_is_gk:
        active_groups = {
            k: v for k, v in scaled.items()
            if k in GK_GROUPS
        }
        candidate_mask = data["Pos"].astype(str).str.upper().str.contains("GK")
    else:
        active_groups = {
            k: v for k, v in scaled.items()
            if k not in GK_GROUPS
        }
        candidate_mask = ~data["Pos"].astype(str).str.upper().str.contains("GK")
    return active_groups, candidate_mask

def perform_search(name: str, target_idx: int, data: pd.DataFrame, active_groups: dict, candidate_mask: pd.DataFrame) -> dict:
    if data.iloc[target_idx]['Min'] < MIN_MINUTES:
        print(f'Warning: {name} has limited minutes. Comparisons may lack accuracy.')
    results = {}
    for group in active_groups:
        X = active_groups[group]
        distances = get_dist(X, target_idx)
        distances[~candidate_mask.to_numpy()] = np.inf
        top_idx = rank_candidates(target_idx, distances)
        results[group] = top_idx
    return results

def format_results(data: pd.DataFrame, results: dict):
    d = {}
    for k, v in results.items():
        d[k] = [data.iloc[i]["Player"] for i in v]
    return d
    
def main():
    # Load, clean, scale data
    raw_data = read_data()
    data = del_dupe_tokens(raw_data)
    numeric_data = get_quantitative(data)
    features = get_feature_groups()
    scaled = scale(features, numeric_data)

    name = input("Enter player name: ")
    target_idx = get_target_idx(name, data)
    target_pos = data.iloc[target_idx]['Pos']
    target_is_gk = 'GK' in str(target_pos).upper()
    active_groups, candidate_mask = filter_pos(target_is_gk, scaled, data)
    candidate_mask = (candidate_mask & data['Min'].ge(MIN_MINUTES))
    results = perform_search(name, target_idx, data, active_groups, candidate_mask)
    named = format_results(data, results)
    print(named)

if __name__ == '__main__':
    main()