from ..db.functions import get_book_by_ISBN, get_book_by_title, add_book_db, update_book_db
from ..recommendation_model.models import recommend_books, recommend_books_by_ISBN, recommend_books_by_title
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

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


@app.get("/get_book")
def get_book(isbn: str):
    # Get the book by ISBN
    book = get_book_by_ISBN(isbn)
    
    # If it doesn't exist, return a message
    if book is None:
        return {"message": "Book not found."}
    
    return book


@app.post("/add_book")
def add_book(book: Book):
    
    # Get the book as a dictionary
    book = book.model_dump(exclude_unset=True)
        
    # Check if the book is in the database
    if get_book_by_ISBN(book["isbn"]) is not None:
        return {"message": "Book already exists. Use /update_book to update the book."}

    # If book isn't in the database, add it
    add_book_db(book)
    
    return {"message": "Book added successfully"}


@app.put("/update_book")
def update_book(isbn: str, new_book: BookUpdate):
    
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
    update_book_db(isbn, new_book)
    
    return {"message": "Book updated successfully"}


@app.get("/get_recommendations")
def get_recommendations(description: str, n: int):
    
    # Get the recommendations
    books = recommend_books(description=description, n=n)

    return books


@app.get("/get_recommendations_by_isbn")
def get_recommendations_by_isbn(isbn: str, n: int):
    
    # Check if the book exists in the database
    if get_book_by_ISBN(isbn) is None:
        return {"message": "Book does not exist. Please use /get_recommendations or /get_recommendations_by_title."}
    
    # Get the recommendations
    books = recommend_books_by_ISBN(ISBN=isbn, n=n)

    return books


@app.get("/get_recommendations_by_title")
def get_recommendations_by_title(title: str, n: int):
    
    # Check if the book exists in the database
    if get_book_by_title(title) is None:
        return {"message": "Book does not exist. Please use /get_recommendations or /get_recommendations_by_isbn."}
    
    # Get the recommendations
    books = recommend_books_by_title(title=title, n=n)

    return books


if __name__ == "__main__":
    uvicorn.run(app, host="localhost")