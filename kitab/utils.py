"""
This module contains utility functions for processing data and generating embeddings.
"""
import numpy as np
import pandas as pd
import math
import os
import pickle as pkl
from sentence_transformers import SentenceTransformer
from .db.db_info import REQUIRED_COLUMNS
from tqdm import tqdm
import logging
from .logger.logger import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def cos_vec_vec(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """
    Compute the cosine similarity between two vectors.
    
    Examples:
        >>> from kitab.utils import cos_vec_vec
        >>> import numpy as np
        >>> vector1 = np.array([1, 2, 3])
        >>> vector2 = np.array([1, 2, 3])
        >>> cos_vec_vec(vector1, vector2)
    
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

def cos_mat_vec(matr: np.ndarray, vect: np.ndarray) -> np.ndarray:
    """
    Compute the cosine similarity between a matrix (consisting of vectors) and a vector.
    
    Examples:
        >>> from kitab.utils import cos_mat_vec
        >>> import numpy as np
        >>> matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> vector = np.array([1, 2, 3])
        >>> cos_mat_vec(matrix, vector)
    
    Parameters:
        matr (np.ndarray): The matrix (containing individual vectors).
        vect (np.ndarray): The vector.
    
    Returns:
        np.ndarray: The cosine similarity between the matrix and the vector.
    """
    dot_product = np.dot(matr, vect)
    norm_vector1 = np.linalg.norm(matr, axis=1)
    norm_vector2 = np.linalg.norm(vect)
    return dot_product / (norm_vector1 * norm_vector2)

def get_embedding(text: str) -> np.ndarray:
    """
    Returns the embedding of the text.
    
    Examples:
        >>> from kitab.utils import get_embedding
        >>> get_embedding(text="Hello, world!")
    
    Parameters:
        text (str): The text to be embedded.
    
    Returns:
        np.ndarray: The embedding of the text.
    """
    return model.encode(text)    
            

# To add in the future: function gets embedding_func: function = None, or gets the embeddings from the user
def process_data(data_file: str, destination_folder: str = "data", column_names: dict[str:str] = None, random_availability: bool = False, chunk_size: int = 20000, verbose: bool = False) -> None:
    """
    Process the given data file, perform data cleaning, and save the processed data and embeddings.
    
    Examples:
        >>> from kitab.utils import process_data
        >>> process_data(data_file="data.csv")

    Parameters:
        data_file (str): The path to the data file.
        destination_folder (str): The path to the destination folder where the processed data and embeddings will be saved.
        column_names (dict[str:str], optional): A dictionary mapping required column names to the corresponding column names in the data file. Defaults to None.
        random_availability (bool, optional): If True, add random book availability to the data. If False, the data must contain an 'availability' column. Defaults to False.
        chunk_size (int, optional): The size of the chunks to split the data into. Defaults to 20000.
        verbose (bool, optional): If True, display log messages. Defaults to False.

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
    
    if verbose:
        logger.info("Data loaded successfully.")
    
    # Make sure all required columns present
    for req_col in REQUIRED_COLUMNS:
        if (column_names and column_names[req_col] not in data.columns) or req_col not in data.columns:
                raise Exception(f"{req_col} column required, but missing in the given data.")
    
    if random_availability:
        # Add random book available
        np.random.seed(42)
        data['available'] = np.random.choice([True, False], size=len(data), p=[0.3, 0.7])
        if verbose:
            logger.info("Available column added.")
    elif (column_names and column_names["available"] not in data.columns) or "available" not in data.columns:
        raise Exception("available column required, but missing in the given data. Either add it, or set random_availability to True.")
    
    if verbose:
        logger.info("All columns available.")

    # Rename the columns to the default column names
    if column_names:
        reverse_mapping = {v: k for k, v in column_names.items()}
        data.rename(columns=reverse_mapping, inplace=True)
    
    # Keep only the required columns
    data = data[REQUIRED_COLUMNS + ["available"]]
    
    # TODO data cleaning here, you need to be able to explain what you did and why
    # Drop NA descriptions
    data = data.dropna(subset=["description"])
    
    split_len = chunk_size
    split_data = [data[idx*split_len:(idx+1)*split_len] for idx in range(math.ceil(len(data)/split_len))]

    if verbose:
        logger.info("Starting computing the embeddings.")
    for idx, d_part in tqdm(enumerate(split_data)):          
        # Save the d_part as a CSV
        d_part.to_csv(f"{destination_folder}/data_{idx}.csv", index=False)
        
        # Generate embeddings for the cleaned descriptions
        embeddings = model.encode(d_part["description"].tolist())

        # Save the embeddings as a pickle file
        with open(f'{destination_folder}/embeddings_{idx}.pkl', 'wb') as f:
            pkl.dump(embeddings, f)
