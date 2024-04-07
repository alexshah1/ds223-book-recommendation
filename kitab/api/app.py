# from recommendation_model.models import *
# from database.database_models import *
import pandas as pd
from fastapi import FastAPI
import uvicorn

# Read the data
data = pd.read_csv("GoodReads_100k_books.csv")

app = FastAPI()

@app.get("/get_book")
def get_book(isbn: str):
    book = data[data["isbn"] == isbn]
    # CRUD operation to get the book from the database
    
    return book.to_dict(orient="records")

@app.post("/add_book")
def add_book(book: object):
    if "isbn" not in book:
        return {"message": "ISBN is required."}
    if book["isbn"] in data["isbn"].values:
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

    # CRUD operation to add the book to the database
    
    return {"message": "Book added successfully"}

@app.put("/update_book")
def update_book(isbn, new_book):
    try:
        if isbn not in data["isbn"].values:
            return {"message": "Book does not exist. Use /add_book to add the book."}
        # CRUD operation to update the book in the database
        return {"message": "Book updated successfully"}
    except Exception as e:
        return {"message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost")