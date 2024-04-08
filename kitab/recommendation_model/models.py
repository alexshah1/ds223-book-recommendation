import numpy as np
import pandas as pd
from ..db.functions import get_table_from_db, get_authors, get_genres
from kitab.utils import get_embedding, cos_mat_vec, cos_vec_vec
    
def recommend_books(description: str, n: int, data : pd.DataFrame = None) -> list:
    
    if data is None:
        data = get_table_from_db("book")
    
    # Check that description is not empty
    if description == "": return []
    
    # Get the embedding of the description
    desc_embedding = get_embedding(description)
    
    # Get all the embeddings for the existing book descriptions
    embeddings = np.stack(data["embedding"].values)

    # Compute cosine similarities
    cosine_similarities = cos_mat_vec(embeddings, desc_embedding)
    
    # Find n most similar books
    most_similar_indices = np.argsort(cosine_similarities)[-n:][::-1]
    
    # Get the ISBNs of the books
    most_similar_books = data.iloc[most_similar_indices]
    most_similar_books.drop(columns=["embedding"], inplace=True)
    ISBNs = most_similar_books["isbn"].tolist()
    
    # Get a dict of authors and genres for the books
    authors = get_authors(ISBNs)
    genres = get_genres(ISBNs)
    
    # Convert the most similar books to a list of dictionaries
    books = most_similar_books.to_dict(orient="records")
    
    # Add the authors and genres to the books
    for book in books:
        book["authors"] = authors[book["isbn"]]
        book["genres"] = genres[book["isbn"]]
        
    # Return the most similar books
    return books


def recommend_books_by_ISBN(ISBN: str, n: int) -> list:
    
    data = get_table_from_db("book")
    
    # Check that ISBN is not empty
    if ISBN == "": return []
    
    # Check that ISBN is in the data
    if ISBN not in data["isbn"].values: return []
    
    # Get the book
    book = data[data["isbn"] == ISBN].iloc[0]
    
    # Return the recommendations
    return recommend_books(book["description"], n, data)


def recommend_books_by_title(title: str, n: int) -> list:
    
    data = get_table_from_db("book")
    
    # Check that title is not empty
    if title == "": return []
    
    # Check that title is in the data
    if title not in data["title"].values: return []
    
    # Get the book
    book = data[data["title"] == title].iloc[0]
    
    # Return the recommendations
    return recommend_books(book["description"], n, data)

