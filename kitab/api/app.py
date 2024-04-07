# from recommendation_model.models import *
# from database.database_models import *
import pandas as pd
from fastapi import FastAPI
import uvicorn

# Read the data
# data = pd.read_csv("GoodReads_100k_books.csv")

app = FastAPI()

@app.get("/get_book")
def get_book(isbn: str):
    pass
    book = get_book_by_ISBN("isbn")
    if book is None:
        return {"message": "Book not found."}
    return book.to_dict(orient="records")

    # book = data[data["isbn"] == isbn]
    # CRUD operation to get the book from the database
    # return book.to_dict(orient="records")
    # return the book

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
    #Check isbn in the database
    if get_book_by_ISBN(book["isbn"]) is not None:
        return {"message": "Book already exists. Use /update_book to update the book."}
    if "title" not in book:
        return {"message": "Title is required."}
    if "description" not in book:
        return {"message": "Description is required."}
    if "author" not in book:
        return {"message": "Author is required."}
    if not isinstance(book["author"], list):
        return {"message": "Author must be a list."}
    if "genres" not in book:
        return {"message": "Genres is required."}
    if not isinstance(book["genres"], list):
        return {"message": "Genres must be a list."}
    
    if set(book.keys()) - {"isbn", "title", "description", "author", "genres"}:
        return {"message": "Invalid keys in the book object."}

    # CRUD operation to add the book to the database
    add_book_to_db(book)
    
    return {"message": "Book added successfully"}

@app.put("/update_book")
def update_book(isbn, new_book):
    try:
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
    except Exception as e:
        return {"message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost")