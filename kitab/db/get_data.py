import pickle
import numpy as np
import pandas as pd
from glob import glob

def get_full_data():
    """
    Retrieves and combines data from multiple CSV files and corresponding pickle files.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the combined data with an additional 'embedding' column.
    """
    data_paths = sorted(glob("GoodReads_Data/*.csv"))
    emg_paths = sorted(glob("GoodReads_Data/*.pkl"))
    
    datas = [pd.read_csv(data_path) for data_path in data_paths]
    embs = []
    
    for emb_path in emg_paths:
        with open(emb_path, "rb") as f:
            emb = pickle.load(f)
        embs.append(emb)
     
    df = pd.concat(datas).reset_index(drop=True)
    df["embedding"] = np.concatenate(embs).tolist()
 
    return df