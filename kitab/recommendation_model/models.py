import numpy as np
import pandas as pd
from ..db.functions import get_table_from_db, get_authors, get_genres
from kitab.utils import get_embedding, cos_mat_vec, cos_vec_vec
    
def recommend_books(description: str, n: int, get_available: bool = True, data : pd.DataFrame = None) -> list[dict]:
    """
    Recommends a list of books based on a given description.
    
    Parameters:
        description (str): The description of the book.
        n (int): The number of books to recommend.
        get_available (bool, optional): Whether to only recommend available books. Defaults to True.
        data (pd.DataFrame, optional): The data containing book information. Defaults to None.
    
    Returns:
        list[dict]: A list of dictionaries representing the most similar books.
    """
    if data is None:
        if get_available:
            data = get_table_from_db("book", conditions={"available": True})
        else:
            data = get_table_from_db("book")
    elif get_available:
        data = data[data["available"] == True]
    
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


def recommend_books_by_ISBN(ISBN: str, n: int, get_available: bool = True) -> list[dict]:
    """
    Recommends a list of books based on the description of the book with the given ISBN.
    
    Parameters:
        ISBN (str): The ISBN of the book.
        n (int): The number of books to recommend.
        get_available (bool, optional): Whether to only recommend available books. Defaults to True.
    
    Returns:
        list[dict]: A list of dictionaries representing the most similar books.
    """
    data = get_table_from_db("book")
    
    # Check that ISBN is not empty
    if ISBN == "": return []
    
    # Check that ISBN is in the data
    if ISBN not in data["isbn"].values: return []
    
    # Get the book
    book = data[data["isbn"] == ISBN].iloc[0]
    
    # Return the recommendations
    return recommend_books(book["description"], n, get_available, data)


def recommend_books_by_title(title: str, n: int, get_available: bool = True) -> list[dict]:
    """
    Recommends a list of books based on the description of the book with the given title.
    
    Parameters:
        title (str): The title of the book.
        n (int): The number of books to recommend.
        get_available (bool, optional): Whether to only recommend available books. Defaults to True.
    
    Returns:
        list[dict]: A list of dictionaries representing the most similar books.
    """    
    data = get_table_from_db("book")
    
    # Check that title is not empty
    if title == "": return []
    
    # Check that title is in the data
    if title not in data["title"].values: return []
    
    # Get the book
    book = data[data["title"] == title].iloc[0]
    
    # Return the recommendations
    return recommend_books(book["description"], n, get_available, data)