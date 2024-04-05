# from recommendation_model.models import search_book
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
    return book.to_dict(orient="records")

@app.post("/add_book")
def add_book(book: object):
    return book

@app.update("/update_book")
def update_book(id, new_book):
    try:
        data[data["id"] == id] = new_book
        return {"message": "Book updated successfully"}
    except Exception as e:
        return {"message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost")