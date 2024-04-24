import numpy as np
from sentence_transformers import SentenceTransformer

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