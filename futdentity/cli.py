import pandas as pd
import numpy as np
from futdentity.data import read_data, del_dupe_tokens, get_quantitative
from futdentity.features import get_feature_groups
from futdentity.similarity import scale, get_dist, rank_candidates, normalize_name

def select_player(matches:np.array) -> int:
    detail_cols = [col for col in ["Squad", "Comp", "Pos"] if col in matches.columns]
    options = matches[["Player", *detail_cols]].reset_index(drop=True)

    print("Multiple players found:")
    for number, (_, player) in enumerate(options.iterrows(), start=1):
        details = ", ".join*(f'{col}: {player[col]}' for col in detail_cols)
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