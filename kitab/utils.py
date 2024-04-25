import numpy as np
import pandas as pd
import math
import os
import pickle as pkl
from sentence_transformers import SentenceTransformer
from .db.db_info import REQUIRED_COLUMNS


model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def cos_vec_vec(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """
    Compute the cosine similarity between two vectors.
    
    Parameters:
    vector1 (np.ndarray): The first vector.
    vector2 (np.ndarray): The second vector.
    
    Returns:
    float: The cosine similarity between the two vectors.
    """
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    return dot_product / (norm_vector1 * norm_vector2)

def cos_mat_vec(vector1: np.ndarray, vector2: np.ndarray) -> np.ndarray:
    """
    Compute the cosine similarity between a matrix (consisting of vectors) and a vector.
    
    Parameters:
    vector1 (np.ndarray): The matrix (containing individual vectors).
    vector2 (np.ndarray): The vector.
    
    Returns:
    np.ndarray: The cosine similarity between the matrix and the vector.
    """
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1, axis=1)
    norm_vector2 = np.linalg.norm(vector2)
    return dot_product / (norm_vector1 * norm_vector2)

def get_embedding(text: str) -> np.ndarray:
    """
    Returns the embedding of the text.
    
    Parameters:
    text (str): The text to be embedded.
    
    Returns:
    np.ndarray: The embedding of the text.
    """
    return model.encode(text)    
            

# To add in the future: function gets embedding_func: function = None, or gets the embeddings from the user
def process_date(data_file: str, destination_folder: str, column_names: dict[str:str] = None, random_availability: bool = False) -> None:
    """
    Process the given data file, perform data cleaning, and save the processed data and embeddings.

    Parameters:
    data_file (str): The path to the data file.
    destination_folder (str): The path to the destination folder where the processed data and embeddings will be saved.
    column_names (dict[str:str], optional): A dictionary mapping required column names to the corresponding column names in the data file. Defaults to None.
    random_availability (bool, optional): If True, add random book availability to the data. If False, the data must contain an 'availability' column. Defaults to False.

    Returns:
        None
    """
    # Check the destination folder
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    elif os.listdir(destination_folder):
        raise Exception(f"Folder '{destination_folder}' is not empty.")
            
    # Load the data
    data = pd.read_csv(data_file)
    
    # Make sure all required columns present
    for req_col in REQUIRED_COLUMNS:
        if (column_names and column_names[req_col] not in data.columns) or req_col not in data.columns:
                raise Exception(f"{req_col} column required, but missing in the given data.")
    
    if random_availability:
        # Add random book availability
        np.random.seed(42)
        data['availability'] = np.random.choice([True, False], size=len(data), p=[0.3, 0.7])
    elif (column_names and column_names["availability"] not in data.columns) or "availability" not in data.columns:
        raise Exception("Availability column required, but missing in the given data. Either add it, or set random_availability to True.")
    
    # Rename the columns to the default column names
    if column_names:
        reverse_mapping = {v: k for k, v in column_names.items()}
        data.rename(columns=reverse_mapping, inplace=True)
    
    # TODO data cleaning here, you need to be able to explain what you did and why
    
    split_len = 20000
    split_data = [data[idx*split_len:(idx+1)*split_len] for idx in range(math.ceil(len(data)/split_len))]

    for idx, d_part in enumerate(split_data):
        
        # Save the d_part as a CSV
        d_part.to_csv(f"{destination_folder}/data_{idx}.csv", index=False)
        
        # Generate embeddings for the cleaned descriptions
        embeddings = model.encode(d_part["description"].tolist())

        # Save the embeddings as a pickle file
        with open(f'{destination_folder}/embeddings_{idx}.pkl', 'wb') as f:
            pkl.dump(embeddings, f)