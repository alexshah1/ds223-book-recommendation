import pickle
import numpy as np
import pandas as pd

def get_full_data():
    datas = []
    embs = []

    for i in range(5):
        data = pd.read_csv(f"GoodReads_Data/data_{i+1}.csv")
        datas.append(data)

        with open(f"GoodReads_Data/embeddings_{i+1}.pkl", "rb") as f:
            emb = pickle.load(f)
        embs.append(emb)
    
    df = pd.concat(datas).reset_index(drop=True)
    df["embedding"] = np.concatenate(embs).tolist()
 
    return df