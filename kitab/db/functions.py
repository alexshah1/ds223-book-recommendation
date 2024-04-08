import pandas as pd
from kitab.utils import get_embedding
from .db_info import user, password, host, database, port
from .sql_interactions import SqlHandler

def get_book_by_ISBN(ISBN: str):
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    # Retrieve the book with the given ISBN
    book = db.get_table("book", conditions={"isbn": ISBN})
    
    if len(book) == 0:
        return None
    
    book_author = db.get_table("bookauthor", conditions={"isbn": ISBN})
    book_genre = db.get_table("bookgenre", conditions={"isbn": ISBN})
        
    # If no book found, return None
    if len(book) == 0:
        return None, None, None
    
    book.drop(columns=["embedding"], inplace=True)
    book = book.to_dict(orient='records')[0]

    author_ids = book_author["author_id"].tolist()
    authors = []
    if len(author_ids) > 0:
        author = db.get_table("author", conditions={"author_id": author_ids})
        authors = author["full_name"].tolist()
    
    genre_ids = book_genre["genre_id"].tolist()
    genres = []
    if len(genre_ids) > 0:
        genre = db.get_table("genre", conditions={"genre_id": genre_ids})
        genres = genre["genre"].tolist()
    
    book["authors"] = authors
    book["genres"] = genres

    # Return the book
    return book


def get_book_by_title(title: str):
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    # Retrieve the book with the given title
    books = db.get_table("book", conditions={"title": title})
    
    print(books)
    
    if len(books) == 0:
        return None
    else:
        ISBN = books["isbn"].values[0]

    # Return the book
    return get_book_by_ISBN(ISBN)


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
    if len(authors) > 0:
        author_ids = _get_or_add_authors(db, authors)
        
        db.insert_records("bookauthor", [{"isbn": ISBN, "author_id": int(author_id)} for author_id in author_ids])
    
    # Add genres to the genres table if doesn't exist
    genres = book["genres"]    
    if len(genres) > 0:
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
    book_author = db.get_table("bookauthor", conditions={"isbn": ISBN})
    book_genre = db.get_table("bookgenre", conditions={"isbn": ISBN})
    
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

def get_authors(ISBNs: list[str]) -> dict:
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    # Retrieve the authors of the books with the given ISBNs
    authors = db.get_table("bookauthor", conditions={"isbn": ISBNs})
    author_ids = authors["author_id"].tolist()
    
    author_table = db.get_table("author", conditions={"author_id": author_ids})
    
    # Initialize dictionary to store authors for each ISBN
    isbn_authors = {isbn: [] for isbn in ISBNs}
    
    # Populate dictionary with authors
    for _, row in authors.iterrows():
        isbn = row["isbn"]
        author_id = row["author_id"]
        author_name = author_table.loc[author_table['author_id'] == author_id, 'full_name'].iloc[0]
        isbn_authors[isbn].append(author_name)
    
    # Return the dictionary of lists
    return isbn_authors

def get_genres(ISBNs: list[str]) -> dict[list]:
    # Open connection to the database
    db = SqlHandler(database, user=user, password=password, host=host, port=port)
    
    # Retrieve the genres of the books with the given ISBNs
    genres = db.get_table("bookgenre", conditions={"isbn": ISBNs})
    genre_ids = genres["genre_id"].tolist()
    
    genre_table = db.get_table("genre", conditions={"genre_id": genre_ids})
    
    # Initialize dictionary to store genres for each ISBN
    isbn_genres = {isbn: [] for isbn in ISBNs}
    
    # Populate dictionary with genres
    for _, row in genres.iterrows():
        isbn = row["isbn"]
        genre_id = row["genre_id"]
        genre_name = genre_table.loc[genre_table['genre_id'] == genre_id, 'genre'].iloc[0]
        isbn_genres[isbn].append(genre_name)
    
    # Return the dictionary of lists
    return isbn_genres