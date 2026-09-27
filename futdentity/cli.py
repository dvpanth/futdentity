import os
import subprocess
import sys
import textwrap
import time
import numpy as np
import pandas as pd

from futdentity.data import del_dupe_tokens, get_quantitative, read_data
from futdentity.features import get_feature_groups
from futdentity.similarity import get_dist, normalize_name, rank_candidates, scale

MIN_MINUTES = 900
GK_GROUPS = {"team_results", "goalkeeping", "goalkeeping_advanced"}
GROUP_DETAILS = {
    "general_playing_time": ("Playing time", "Appearances, starts, and minutes"),
    "shooting": ("Shooting", "Goals, assists, expected output, and shots"),
    "passing": ("Passing", "Pass volume, progression, and delivery"),
    "chance_creation": ("Chance creation", "Shot-creating and goal-creating actions"),
    "defense": ("Defense", "Tackles, interceptions, clearances, and errors"),
    "possession_carrying": ("Possession & carrying", "Touches, take-ons, carries, and receptions"),
    "fouls_recovery_aerials": ("Fouls, recoveries & aerials", "Fouls, recoveries, and aerial duels won"),
    "team_results": ("Team results", "Wins, draws, and losses"),
    "goalkeeping": ("Goalkeeping", "Goals conceded, shots faced, saves, and clean sheets"),
    "goalkeeping_advanced": ("Advanced goalkeeping", "Distribution, crosses, and sweeping activity"),
}

def styled(text: str, color: str = "36") -> str:
    if sys.stdout.isatty() and "NO_COLOR" not in os.environ:
        return f"\033[{color}m{text}\033[0m"
    return text

def clear_screen():
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)

def heading(title: str) -> None:
    print(f"\n{styled(title, '1;36')}")
    print("-" * 68)

def show_hero() -> None:
    print(styled("\n  F U T D E N T I T Y", "1;36"))
    print("  Find a familiar game in a different player.")
    print("  2024-25 | Europe's top five leagues | Statistical similarity")

def read_choice(prompt: str, maximum: int) -> int:
    while True:
        choice = input(prompt).strip()
        if choice.isascii() and choice.isdigit() and 0 <= int(choice) <= maximum:
            return int(choice)
        print(f"Please enter a number from 0 to {maximum}.")

def select_player(matches: pd.DataFrame) -> int | None:
    heading("Choose a player record")
    print("This name appears in more than one record. Choose the squad to compare.")
    for number, (_, player) in enumerate(matches.iterrows(), start=1):
        print(f"\n  {number}. {player['Player']} | {player['Squad']}")
        print(f"     {player['Comp']} | {player['Pos']} | {int(player['Min']):,} min")
    print("\n  0. Back to player search")
    choice = read_choice("\nSelect a record: ", len(matches))
    return None if choice == 0 else int(matches.index[choice - 1])

def get_target_idx(name: str, data: pd.DataFrame) -> int | None:
    matches = data[data["Player"].map(normalize_name) == normalize_name(name)]
    if matches.empty:
        raise ValueError(f'No player found named "{name}".')
    if len(matches) > 1:
        return select_player(matches)
    return int(matches.index[0])

def filter_pos(target_is_gk: bool, scaled: dict, data: pd.DataFrame) -> tuple[dict, pd.Series]:
    goalkeeper_mask = data["Pos"].astype(str).str.upper().str.contains("GK")
    active_groups = {
        group: values for group, values in scaled.items()
        if (group in GK_GROUPS) == target_is_gk
    }
    return active_groups, goalkeeper_mask if target_is_gk else ~goalkeeper_mask

def perform_search(target_idx: int, active_groups: dict, candidate_mask: pd.Series) -> dict:
    """Return eligible row positions and distances for each requested group."""
    results = {}
    for group, values in active_groups.items():
        distances = get_dist(values, target_idx)
        distances[~candidate_mask.to_numpy()] = np.inf
        indices = rank_candidates(target_idx, distances)
        results[group] = {"indices": indices, "distances": distances[indices]}
    return results

def display_results(data: pd.DataFrame, results: dict) -> None:
    clear_screen()
    for group, result in results.items():
        label, _ = GROUP_DETAILS[group]
        heading(f"Most similar | {label}")
        if len(result["indices"]) == 0:
            print("No eligible players with complete statistics for this category.")
            continue
        for rank, (idx, distance) in enumerate(
            zip(result["indices"], result["distances"]), start=1
        ):
            player = data.iloc[int(idx)]
            print(f"\n  {styled(str(rank) + '.', '1')} {styled(player['Player'], '1')}")
            print(
                f"     {player['Squad']} | {player['Pos']} | "
                f"{int(player['Min']):,} min | Distance {distance:.3f}"
            )
        print("\n  Lower distance means closer statistics within this category.")

def browse_categories(target_idx: int, data: pd.DataFrame, scaled: dict) -> None:
    clear_screen()
    player = data.iloc[target_idx]
    active_groups, candidate_mask = filter_pos(
        "GK" in str(player["Pos"]).upper(), scaled, data
    )
    candidate_mask &= data["Min"].ge(MIN_MINUTES)
    groups = list(active_groups)
    while True:
        clear_screen()
        heading(f"Compare {player['Player']}")
        print(f"{player['Squad']} | {player['Pos']} | {int(player['Min']):,} min")
        print(f"Candidates: same goalkeeper/outfield class, {MIN_MINUTES:,}+ minutes.")
        if player["Min"] < MIN_MINUTES:
            print(styled("Limited minutes: this player's totals may be less representative.", "33"))
        print("\nChoose the aspect of their game you want to compare:\n")
        for number, group in enumerate(groups, start=1):
            label, description = GROUP_DETAILS[group]
            print(f"  {number}. {label}\n     {description}")
        print(f"\n  {len(groups) + 1}. View all categories")
        print("  0. Back to main menu")
        choice = read_choice("\nSelect a category: ", len(groups) + 1)
        if choice == 0:
            return
        selected = active_groups if choice == len(groups) + 1 else {
            groups[choice - 1]: active_groups[groups[choice - 1]]
        }
        results = perform_search(target_idx, selected, candidate_mask)
        clear_screen()
        display_results(data, results)
        input("\nPress Enter to choose another category...")

def search_players(data: pd.DataFrame, scaled: dict) -> None:
    clear_screen()
    heading("Search for similar players")
    print("Enter a full player name. Accents and capitalization are optional.")
    print("For example: Lamine Yamal, Kylian Mbappe, or Thibaut Courtois.")
    print("Leave the name blank to return to the main menu.")
    while True:
        name = input("\nPlayer name: ").strip()
        clear_screen()
        if not name:
            return
        try:
            target_idx = get_target_idx(name, data)
        except ValueError as error:
            heading("Search for similar players")
            print(error)
            print("Check the spelling or try another player from the 2024-25 dataset.")
            continue
        if target_idx is None:
            clear_screen()
            heading("Search for similar players")
            print("Enter a full player name, or leave it blank for the main menu.")
            continue
        browse_categories(target_idx, data, scaled)
        return

def show_how_it_works() -> None:
    clear_screen()
    heading("How Futdentity works")
    paragraphs = [
        "Each player is represented by their statistics in a selected category. "
        "The statistics are standardized across the dataset so large numerical "
        "scales do not dominate the comparison. Euclidean distance then finds "
        "players with the closest statistical profiles.",
        f"Results exclude the selected record and players below {MIN_MINUTES:,} "
        "minutes. Goalkeepers and outfield players have separate candidate pools. "
        "Missing or non-finite distances are excluded, so some searches may return "
        "fewer than five matches.",
        "V1 uses mostly season totals, with some per-90 rates. Minutes played and "
        "team context can influence the results. Outfield candidates are not "
        "restricted to the same position. These are statistical similarities, "
        "not ratings of player quality or validated scouting recommendations.",
        "Distances describe similarity within a category; they are not percentages "
        "and should not be compared across categories. A player listed for multiple "
        "squads has separate records. The search excludes only the selected record.",
    ]
    for paragraph in paragraphs:
        print(textwrap.fill(paragraph, width=68))
        print()
    input("Press Enter to return to the main menu...")

def main() -> None:
    data = None
    scaled = None
    try:
        while True:
            clear_screen()
            show_hero()
            heading("Main menu")
            print("  1. Search for similar players")
            print("  2. How it works")
            print("  0. Exit")
            choice = read_choice("\nChoose an option: ", 2)
            if choice == 0:
                break
            if choice == 2:
                show_how_it_works()
                continue
            if data is None:
                print("\nLoading player statistics...")
                time.sleep(2)
                try:
                    data = del_dupe_tokens(read_data()).reset_index(drop=True)
                    scaled = scale(get_feature_groups(), get_quantitative(data))
                except (OSError, ValueError, KeyError) as error:
                    print(f"Could not load the player dataset: {error}")
                    data = None
                    input("Press Enter to return to the main menu...")
                    continue
            search_players(data, scaled)
    except (KeyboardInterrupt, EOFError):
        print()
    print("\nThanks for exploring with Futdentity.")

if __name__ == "__main__":
    main()