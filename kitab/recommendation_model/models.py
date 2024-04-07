import numpy as np
import pandas as pd
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


def recommend_book(description: str, n: int, data : pd.DataFrame = None) -> list:
    
    if data is None:
        data = get_table_from_db("books")
    
    # Check that description is not empty
    if description == "": return []
    
    # Get the embedding of the description
    desc_embedding = model.encode(description)
    
    # Get all the embeddings for the existing book descriptions
    embeddings = data["embedding"].tolist()

    # Compute cosine similarities
    cosine_similarities = cos_mat_vec(embeddings, desc_embedding)
    
    # Find n most similar books
    most_similar_indices = np.argsort(cosine_similarities)[-n:][::-1]
    
    # Get the ISBNs of the books
    most_similar_books = data.iloc[most_similar_indices]
    
    # Return the most similar books
    return most_similar_books


def recommend_book_by_ISBN(ISBN: str, n: int) -> list:
    
    data = get_table_from_db("books")
    
    # Check that ISBN is not empty
    if ISBN == "": return []
    
    # Check that ISBN is in the data
    if ISBN not in data["isbn"].values: return []
    
    # Get the book
    book = data[data["isbn"] == ISBN].iloc[0]
    
    # Return the recommendations
    return recommend_book(book["desc"], n, data)


def recommend_book_by_title(title: str, n: int) -> list:
    
    data = get_table_from_db("books")
    
    # Check that title is not empty
    if title == "": return []
    
    # Check that title is in the data
    if title not in data["title"].values: return []
    
    # Get the book
    book = data[data["title"] == title].iloc[0]
    
    # Return the recommendations
    return recommend_book(book["desc"], n, data)

