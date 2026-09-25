import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import unicodedata

RANK=5

def scale(feature_groups: dict, data: pd.DataFrame) -> dict:
    scaled_groups = {}
    for feature_group, features in feature_groups.items():
        feature_data = data[features].copy()
        scaler = StandardScaler()
        group_scaled = pd.DataFrame(
            scaler.fit_transform(feature_data),
            columns=features,
            index=feature_data.index
        )
        scaled_groups[feature_group] = group_scaled
    return scaled_groups

def get_dist(X:pd.DataFrame, target_idx:int) -> np.array:
    target_vec = X.iloc[target_idx].values
    distances = np.linalg.norm(X.values - target_vec, axis=1)
    return distances

def rank_candidates(target_idx:int, distances:np.array):
    distances[target_idx] = np.inf
    distances[~np.isfinite(distances)] = np.inf
    valid_idx = np.flatnonzero(np.isfinite(distances))
    top_idx = valid_idx[np.argsort(distances[valid_idx])[:RANK]]
    return top_idx

def normalize_name(name:str) -> str:
    name = str(name).lower().strip()
    name = unicodedata.normalize("NFKD", name)
    name = "".join(char for char in name if not unicodedata.combining(char))
    return name.casefold().strip()