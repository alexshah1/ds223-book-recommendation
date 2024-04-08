import pandas as pd
from ..recommendation_model.model_utils import get_embedding
from .db_info import user, password, host, database, port
from .sql_interactions import SqlHandler

def get_book_by_ISBN(ISBN: str):
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    # Retrieve the book with the given ISBN
    book = db.get_table("book")
    book_author = db.get_table("bookauthor")
    book_genre = db.get_table("bookgenre")
    author = db.get_table("author")
    genre = db.get_table("genre")

    book = book[book["isbn"] == ISBN]
    
    # If no book found, return None
    if len(book) == 0:
        return None
    
    book.drop(columns=["embedding"], inplace=True)
    book = book.to_dict("records")

    author_ids = book_author[book_author["isbn"] == ISBN]["author_id"].tolist()
    authors = author[author["author_id"].isin(author_ids)]["full_name"].tolist()
    
    genre_ids = book_genre[book_genre["isbn"] == ISBN]["genre_id"].tolist()
    genres = genre[genre["genre_id"].isin(genre_ids)]["genre"].tolist()

    # Return the book
    return book, authors, genres

def add_book_db(book: dict) -> None:
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
        
    # Extract information from the book dictionary
    ISBN = book["ISBN"]
    title = book["title"]
    description = book["description"]
    available = book["available"]
    embedding = get_embedding(book["description"]).tolist()
    
    db.insert_records("book", [{"isbn": ISBN, "title": title, "description": description, "embedding": embedding, "available": available}])
    
    # Add author(s) to the author table if doesn't exist
    authors = book["authors"]
    author_ids = _get_or_add_authors(db, authors)
    
    db.insert_records("bookauthor", [{"isbn": ISBN, "author_id": int(author_id)} for author_id in author_ids])
    
    # Add genres to the genres table if doesn't exist
    genres = book["genres"]    
    genre_ids = _get_or_add_genres(db, genres)
    
    db.insert_records("bookgenre", [{"isbn": ISBN, "genre_id": int(genre_id)} for genre_id in genre_ids])
    
def update_book_db(ISBN: str, new_book: dict):
    
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    condition = {"ISBN": ISBN}
    new_values = {}
    
    latest_ISBN = ISBN
    
    for key in new_book.keys():
        if key in ["ISBN", "title", "description", "available"]:
            new_values[key] = new_book[key]
        if key == "ISBN":
            latest_ISBN = new_book["ISBN"]
        if key == "description":
            new_values["embedding"] = get_embedding(new_book["description"]).tolist()

    db.update_records("book", new_values, condition)
    
    ISBN = latest_ISBN
    
    # Get the tables
    book_author = db.get_table("bookauthor")
    book_genre = db.get_table("bookgenre")
    
    # Add author(s) to the author table if doesn't exist
    if "authors" in new_book:
        authors = new_book["authors"]
        new_author_ids = set(_get_or_add_authors(db, authors))
        current_author_ids = set(book_author[book_author["isbn"] == ISBN]["author_id"].tolist())
        
        removed_authors = current_author_ids - new_author_ids
        added_authors = new_author_ids - current_author_ids
        
        db.remove_records("bookauthor", [{"isbn": ISBN, "author_id": int(removed_author)} for removed_author in removed_authors])
        db.insert_records("bookauthor", [{"isbn": ISBN, "author_id": int(added_author)} for added_author in added_authors])
    
    # Add genres to the genres table if doesn't exist
    if "genres" in new_book:
        genres = new_book["genres"]    
        new_genre_ids = set(_get_or_add_genres(db, genres))
        current_genre_ids = set(book_genre[book_genre["isbn"] == ISBN]["genre_id"].tolist())
    
        removed_genres = current_genre_ids - new_genre_ids
        added_genres = new_genre_ids - current_genre_ids
        
        db.remove_records("bookgenre", [{"isbn": ISBN, "genre_id": int(removed_genre)} for removed_genre in removed_genres])
        db.insert_records("bookgenre", [{"isbn": ISBN, "genre_id": int(added_genre)} for added_genre in added_genres])
    

def get_table_from_db(table_name: str) -> pd.DataFrame:
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    # Retrieve the table from the database
    table = db.get_table(table_name)
    
    # Return the table
    return table

def _get_or_add_genres(db: SqlHandler, genres: str) -> int:
    genre_table = db.get_table("genre")
    
    genre_ids = []
    cur_index = max(genre_table["genre_id"] + 1)
    to_insert = []
    
    for genre in genres:
        if genre in genre_table["genre"].values:
            genre_id = genre_table[genre_table["genre"] == genre]["genre_id"].values[0]
        else:
            genre_id = cur_index
            cur_index += 1
            to_insert.append({"genre_id": genre_id, "genre": genre})
        genre_ids.append(genre_id)
    
    # Insert the records
    db.insert_records("genre", to_insert)
    return genre_ids

def _get_or_add_authors(db: SqlHandler, authors: str) -> int:
    author_table = db.get_table("author")
    
    author_ids = []
    cur_index = max(author_table["author_id"]+1)
    to_insert = []
    
    for author in authors:
        if author in author_table["full_name"].values:
            author_id = author_table[author_table["full_name"] == author]["author_id"].values[0]
        else:
            author_id = cur_index
            cur_index += 1
            to_insert.append({"author_id": author_id, "full_name": author})
        author_ids.append(author_id)
    
    # Insert the records
    db.insert_records("author", to_insert)
    return author_ids


