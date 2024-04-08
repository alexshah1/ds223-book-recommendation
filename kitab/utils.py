import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def cos_vec_vec(vector1: np.ndarray, vector2: np.ndarray) -> float:
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    return dot_product / (norm_vector1 * norm_vector2)

def cos_mat_vec(vector1: np.ndarray, vector2: np.ndarray) -> float:
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1, axis=1)
    norm_vector2 = np.linalg.norm(vector2)
    return dot_product / (norm_vector1 * norm_vector2)

def get_embedding(text: str) -> np.ndarray:
    return model.encode(text)