from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REMOVE_COLS = ['Rk']
DUPLICATE_COLS = [
    'Rk', 'Age', 'Born', '90s', 'Gls', 'PK', 'PKatt', 'xG', 'npxG', 'Ast', 'xAG', 'PrgP', 'Att', 'Crs',
    'Off', 'Blocks', 'Fld', 'Sh', 'Int', 'TklW', 'PrgC', 'PrgR', 'TotDist', 'PrgDist', '1/3', 'MP',
    'Min', 'Starts', 'CrdY', 'CrdR', 'Lost'
    ]

def read_data(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / 'playerdata_2425.csv')

def del_dupe_tokens(data):
    cleaned = data.copy()
    for token in DUPLICATE_COLS:
        cleaned = cleaned.loc[:, cleaned.columns.str.contains(f'^{token}$') | ~cleaned.columns.str.contains(token)]

    return cleaned.drop(columns=REMOVE_COLS)

def get_quantitative(data):
    return data[data.select_dtypes(include=[np.number]).columns.tolist()].copy()