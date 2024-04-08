from ..db.functions import get_book_by_ISBN, add_book_db, update_book_db
import pandas as pd
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/get_book")
def get_book(isbn: str):
    pass
    book, authors, genres = get_book_by_ISBN("isbn")
    if book is None:
        return {"message": "Book not found."}
    book = book.to_dict(orient="records")
    book["authors"] = authors
    book["genres"] = genres
    return book

@app.get("/get_recommendations")
def get_recommendations(desc: str, n: int):
    pass
    # USE the recommendation model to get the recommendations
    # return recommendations
    
@app.get("/get_recommendations_by_isbn")
def get_recommendations_by_isbn(isbn: str, n: int):
    pass
    # USE the recommendation model to get the recommendations
    # return recommendations
    
@app.get("/get_recommendations_by_title")
def get_recommendations_by_title(title: str, n: int):
    pass
    # USE the recommendation model to get the recommendations
    # return recommendations

@app.post("/add_book")
def add_book(book: object):
    if "isbn" not in book:
        return {"message": "ISBN is required."}
    
    #Check ISBN is in the database
    if get_book_by_ISBN(book["isbn"]) is not None:
        return {"message": "Book already exists. Use /update_book to update the book."}
    if "title" not in book:
        return {"message": "Title is required."}
    if "description" not in book:
        return {"message": "Description is required."}
    if "authors" not in book:
        return {"message": "Authors is required."}
    if not isinstance(book["authors"], list):
        return {"message": "Authors must be a list."}
    if "genres" not in book:
        return {"message": "Genres is required."}
    if not isinstance(book["genres"], list):
        return {"message": "Genres must be a list."}
    
    if set(book.keys()) - {"isbn", "title", "description", "author", "genres"}:
        return {"message": "Invalid keys in the book object."}

    add_book_db(book)
    
    return {"message": "Book added successfully"}

@app.put("/update_book")
def update_book(isbn, new_book):
    # Check isbn in the database
    if get_book_by_ISBN(isbn) is None:
        return {"message": "Book does not exist. Use /add_book to add the book."}
    # CRUD operation to update the book in the database
    
    if "author" in new_book and not isinstance(new_book["author"], list):
        return {"message": "Author must be a list."}
    if "genres" not in new_book and not isinstance(new_book["genres"], list):
        return {"message": "Genres must be a list."}

    if set(new_book.keys()) - {"isbn", "title", "description", "author", "genres"}:
        return {"message": "Invalid keys in the book object."}

    update_book_db(isbn, new_book)
    
    return {"message": "Book updated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost")