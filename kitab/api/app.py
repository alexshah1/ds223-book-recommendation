"""
This module contains the API for the book recommendation system.
"""
from ..db.functions import get_book_by_ISBN, get_book_by_title, add_book_db, update_book_db, add_recommendation_log, get_history_by_recommendation_isbn
from ..recommendation_model.models import recommend_books, recommend_books_by_ISBN, recommend_books_by_title
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import logging
from ..logger.logger import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

app = FastAPI()

class Book(BaseModel):
    isbn: str
    title: str
    description: str 
    available: bool
    authors: list[str]
    genres: list[str]
    
    class Config:
        extra = "forbid"
        
        
class BookUpdate(BaseModel):
    isbn: str | None = None
    title: str | None = None
    description: str | None = None
    available: bool | None = None
    authors: list[str] | None = None
    genres: list[str] | None = None
    
    class Config:
        extra = "forbid"


@app.get("/get_book_by_isbn")
def get_book_isbn(isbn: str):
    """
    Get the book by ISBN.
    
    Parameters:
    ISBN (str): The ISBN of the book.

    Returns:
    dict: The book information.
    """
    # Get the book by ISBN
    book = get_book_by_ISBN(isbn)
    
    # If it doesn't exist, return a message
    if book is None:
        return {"message": "Book not found."}
    
    return book


@app.get("/get_book_by_title")
def get_book_title(title: str):
    """
    Get the book by title.
    
    Parameters:
    title (str): The title of the book.

    Returns:
    dict: The book information.
    """
    # Get the book by ISBN
    book = get_book_by_title(title)
    
    # If it doesn't exist, return a message
    if book is None:
        return {"message": "Book not found."}
    
    return book


@app.post("/add_book")
def add_book(book: Book):
    """
    Add a book to the database.
    
    Parameters:
    book (dict): The book information.
    """
    # Get the book as a dictionary
    book = book.model_dump(exclude_unset=True)
        
    # Check if the book is in the database
    if get_book_by_ISBN(book["isbn"]) is not None:
        return {"message": "Book already exists. Use /update_book to update the book."}

    # If book isn't in the database, add it
    if add_book_db(book):
        return {"message": "Book added successfully"}
    
    return {"message": "Something went wrong. Book not added."}


@app.put("/update_book")
def update_book(isbn: str, new_book: BookUpdate):
    """
    Update a book in the database.
    
    Parameters:
    ISBNs (str): The ISBN of the book.
    new_book (dict): The new book information.
    """
    # If book isn't in the database, return a message
    if get_book_by_ISBN(isbn) is None:
        return {"message": "Book does not exist. Use /add_book to add the book."}
    
    # Get the set fields
    set_fields = new_book.model_dump(exclude_unset=True)
    
    # If no fields have been set, return a message
    if len(set_fields.keys()) == 0:
        return {"message": "Nothing passed."}
    
    # Compare the old book with the new one
    new_book = new_book.model_dump()
    old_book= get_book_by_ISBN(isbn)
    
    # Remove unchanged fields
    to_remove = []
    for field in new_book:
        if old_book[field] == new_book[field] or new_book[field] is None:
            to_remove.append(field)
            
    for field in to_remove:
        new_book.pop(field)

    # If no fields to be changed remained, return a message
    if len(new_book.keys()) == 0:
        return {"message": "Nothing new passed."}

    # Update the book
    if update_book_db(isbn, new_book):
        return {"message": "Book updated successfully"}
    
    return {"message": "Something went wrong. Book not updated."}


@app.get("/get_recommendations")
def get_recommendations(description: str, n: int, get_available: bool = True):
    """
    Return n book recommendations based on the description.
    
    Parameters:
    description (str): The description of the book.
    n (int): The number of recommendations to return.
    get_available (bool, optional): Whether to only recommend available books. Defaults to True.
    
    Returns:
    dict: The recommendations.
    """
    # Get the recommendations
    books = recommend_books(description=description, n=n, get_available=get_available)

    return books


@app.get("/get_recommendations_by_isbn")
def get_recommendations_by_isbn(isbn: str, n: int, get_available: bool = True):
    """
    Return n book recommendations based on recommendation of the book with the given ISBN.
    
    Parameters:
    ISBN (str): The ISBN of the book.
    n (int): The number of recommendations to return.
    get_available (bool, optional): Whether to only recommend available books. Defaults to True.
    
    Returns:
    dict: The recommendations.
    """
    # Check if the book exists in the database
    if get_book_by_ISBN(isbn) is None:
        return {"message": "Book does not exist. Please use /get_recommendations or /get_recommendations_by_title."}
    
    # Get the recommendations
    books = recommend_books_by_ISBN(ISBN=isbn, n=n, get_available=get_available)

    return books


@app.get("/get_recommendations_by_title")
def get_recommendations_by_title(title: str, n: int, get_available: bool = True):
    """
    Return n book recommendations based on recommendation of the book with the given title.
    
    Parameters:
    title (str): The title of the book.
    n (int): The number of recommendations to return.
    get_available (bool, optional): Whether to only recommend available books. Defaults to True.
    
    Returns:
    dict: The recommendations.
    """
    # Check if the book exists in the database
    if get_book_by_title(title) is None:
        return {"message": "Book does not exist. Please use /get_recommendations or /get_recommendations_by_isbn."}
    
    # Get the recommendations
    books = recommend_books_by_title(title=title, n=n, get_available=get_available)

    return books


@app.get("/get_logs")
def get_logs(recommendation_isbn: str):
    """
    Return the history of recommendations for the book with the given ISBN.
    
    Parameters:
    recommendation_isbn (str): The ISBN of the book.
    
    Returns:
    dict: The history of recommendations.
    """
    # Check if the book is in the database
    if get_book_by_ISBN(recommendation_isbn) is None:
        return {"message": "No book with the given ISBN in the database."}
    
    return get_history_by_recommendation_isbn(recommendation_isbn)
    

@app.post("/add_log")
def add_log(description: str, recommendation_isbn: str, successful: bool):
    """
    Add a log of a recommendation.
    
    Parameters:
    description (str): The description of the book.
    recommendation_isbn (str): The ISBN of the recommended book.
    successful (bool): Whether the recommendation was successful.
    """        
    # Check if the book is in the database
    if get_book_by_ISBN(recommendation_isbn) is None:
        return {"message": "No book with the given ISBN in the database."}

    # If book isn't in the database, add it
    if add_recommendation_log(description, recommendation_isbn, successful):
        return {"message": "Log successfully added."}
    
    return {"message": "Something went wrong. Log not added."}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost")