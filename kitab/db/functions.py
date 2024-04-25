"""
This module contains tailored functions for interacting with the database. These are used by the API and the recommendation model.
"""
import pandas as pd
from kitab.utils import get_embedding
from .db_info import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from .sql_interactions import SqlHandler
import logging

from ..logger.logger import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def get_book_by_ISBN(ISBN: str):
    """
    Retrieves a book from the database based on its ISBN.

    Parameters:
    ISBN (str): The ISBN of the book to retrieve.

    Returns:
    dict or None: A dictionary containing the book information if found, or None if no book is found.
    """

    # Open connection to the database
    db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logging.info("Database connection opened.")
    
    # Retrieve the book with the given ISBN
    book = db.get_table("book", conditions={"isbn": ISBN})
    
    if len(book) == 0:
        logging.info("Book not found.")
        return None
    logging.info("Book retrieved.")
    
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
        logging.info(f"Authors retrieved.")
    else:
        logging.info("No authors found.")
    
    genre_ids = book_genre["genre_id"].tolist()
    genres = []
    if len(genre_ids) > 0:
        genre = db.get_table("genre", conditions={"genre_id": genre_ids})
        genres = genre["genre"].tolist()
        logging.info(f"Genres retrieved.")
    else:
        logging.info("No genres found.")
    
    book["authors"] = authors
    book["genres"] = genres

    # Return the book
    return book


def get_book_by_title(title: str):
    """
    Retrieves a book from the database based on its title.

    Parameters:
    title (str): The title of the book to retrieve.

    Returns:
    dict or None: A dictionary containing the book information if found, or None if no book is found.
    """
    # Open connection to the database
    db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logging.info("Database connection opened.")
    
    # Retrieve the book with the given title
    books = db.get_table("book", conditions={"title": title})
    
    print(books)
    
    if len(books) == 0:
        logging.info("Book not found.")
        return None
    else:
        logging.info("Book ISBN retrieved.")
        ISBN = books["isbn"].values[0]

    # Return the book
    return get_book_by_ISBN(ISBN)


def add_book_db(book: dict) -> bool:
    """
    Adds a book to the database.

    Parameters:
    book (dict): A dictionary containing the book information.
    
    Returns:
    bool: True if the book was successfully added, False otherwise.
    """
    try:
        # Open connection to the database
        db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        logging.info("Database connection opened.")
            
        # Extract information from the book dictionary
        ISBN = book["isbn"]
        title = book["title"]
        description = book["description"]
        available = book["available"]
        embedding = get_embedding(book["description"]).tolist()
        
        db.insert_records("book", [{"isbn": ISBN, "title": title, "description": description, "embedding": embedding, "available": available}])
        logging.info("Book table populated.")
        
        # Add author(s) to the author table if doesn't exist
        authors = book["authors"]
        if len(authors) > 0:
            logging.info("Authors to be added.")
            author_ids = _get_or_add_authors(db, authors)
            
            db.insert_records("bookauthor", [{"isbn": ISBN, "author_id": int(author_id)} for author_id in author_ids])
            logging.info("Author table populated.")
        else:
            logging.info("No authors to be added.")
        
        # Add genres to the genres table if doesn't exist
        genres = book["genres"]    
        if len(genres) > 0:
            logging.info("Genres to be added.")
            genre_ids = _get_or_add_genres(db, genres)
            
            db.insert_records("bookgenre", [{"isbn": ISBN, "genre_id": int(genre_id)} for genre_id in genre_ids])
            logging.info("Genre table populated.")
        else:
            logging.info("No genres to be added.")

        return True
    except:
        return False    
    
def update_book_db(ISBN: str, new_book: dict) -> bool:
    """
    Updates a book in the database.
    
    Parameters:
    ISBN (str): The ISBN of the book to update.
    new_book (dict): A dictionary containing the updated book information.
    
    Returns:
    bool: True if the book was successfully updated, False otherwise.
    """
    try:
        # Open connection to the database
        db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        logging.info("Database connection opened.")
        
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
        logging.info("Book table updated.")
        
        ISBN = latest_ISBN
        
        # Get the tables
        book_author = db.get_table("bookauthor", conditions={"isbn": ISBN})
        book_genre = db.get_table("bookgenre", conditions={"isbn": ISBN})
        
        # Add author(s) to the author table if doesn't exist
        if "authors" in new_book:
            logging.info("Authors to be updated.")
            
            authors = new_book["authors"]
            new_author_ids = set(_get_or_add_authors(db, authors))
            current_author_ids = set(book_author[book_author["isbn"] == ISBN]["author_id"].tolist())
            
            removed_authors = current_author_ids - new_author_ids
            added_authors = new_author_ids - current_author_ids
            
            db.remove_records("bookauthor", [{"isbn": ISBN, "author_id": int(removed_author)} for removed_author in removed_authors])
            db.insert_records("bookauthor", [{"isbn": ISBN, "author_id": int(added_author)} for added_author in added_authors])
            
            logging.info("Author table updated.")
        else:
            logging.info("No authors to be updated.")
        
        # Add genres to the genres table if doesn't exist
        if "genres" in new_book:
            logging.info("Genres to be updated.")
            
            genres = new_book["genres"]    
            new_genre_ids = set(_get_or_add_genres(db, genres))
            current_genre_ids = set(book_genre[book_genre["isbn"] == ISBN]["genre_id"].tolist())
        
            removed_genres = current_genre_ids - new_genre_ids
            added_genres = new_genre_ids - current_genre_ids
            
            db.remove_records("bookgenre", [{"isbn": ISBN, "genre_id": int(removed_genre)} for removed_genre in removed_genres])
            db.insert_records("bookgenre", [{"isbn": ISBN, "genre_id": int(added_genre)} for added_genre in added_genres])
            
            logging.info("Genre table updated.")
        else:
            logging.info("No genres to be updated.")
            
        return True
    except:
        return False

def get_table_from_db(table_name: str, conditions: dict = None) -> pd.DataFrame:
    """
    Retrieves a table from the database.

    Parameters:
    table_name (str): The name of the table to retrieve.
    conditions (dict): A dictionary of conditions to filter the table.

    Returns:
    pd.DataFrame: A DataFrame containing the table information.
    """
    # Open connection to the database
    db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logging.info("Database connection opened.")
    
    # Retrieve the table from the database
    if conditions:
        table = db.get_table(table_name, conditions=conditions)
    else:
        table = db.get_table(table_name)
        
    logging.info(f"Table {table_name} retrieved.")
    
    # Return the table
    return table

def _get_or_add_genres(db: SqlHandler, genres: list[str]) -> list[int]:
    """
    Get the genre IDs for the given list of genres. If the genres do not exist in the database, add them to the genre table.

    Parameters:
    db (SqlHandler): The database handler.
    genres (list[str]): A list of genres.

    Returns:
    list[int]: A list of genre IDs.
    """
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
    logging.info("New genres added.")
    
    return genre_ids

def _get_or_add_authors(db: SqlHandler, authors: list[str]) -> list[int]:
    """
    Get the author IDs for the given list of authors. If the authors do not exist in the database, add them to the author table.

    Parameters:
    db (SqlHandler): The database handler.
    authors (list[str]): A list of authors.

    Returns:
    list[int]: A list of author IDs.
    """
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
    logging.info("New authors added.")
    
    return author_ids

def get_authors(ISBNs: list[str]) -> dict[str:list]:
    """
    Get the authors for the given list of ISBNs.
    
    Parameters:
    ISBNs (list[str]): A list of ISBNs.

    Returns:
    dict[str:list]: A dictionary containing the authors for each ISBN.
    """
    # Open connection to the database
    db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logging.info("Database connection opened.")
    
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
    """
    Get the genres for the given list of ISBNs.
    
    Parameters:
    ISBNs (list[str]): A list of ISBNs.

    Returns:
    dict[str:list]: A dictionary containing the genres for each ISBN.
    """
    # Open connection to the database
    db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logging.info("Database connection opened.")

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


def get_history_by_recommendation_isbn(recommendation_isbn: str) -> dict:
    """
    Get the history of recommendations for a book with the given ISBN.
    
    Parameters:
    recommendation_ISBN (str): The ISBN of the recommended book.

    Returns:
    dict: A dictionary containing the history of recommendations for the book.
    """
    # Open connection to the database
    db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logging.info("Database connection opened.")
    
    # Retrieve the history of books that have been recommended
    history = db.get_table("history", conditions={"recommendation_ISBN": recommendation_isbn})
    
    # Return the history
    return history.drop(columns="log_id").to_dict(orient='records')


def add_recommendation_log(description: str, recommendation_ISBN: str, successful: bool) -> bool:
    """
    Adds a recommendation log to the history table.
    
    Parameters:
    description (str): The description of the recommendation.
    recommendation_ISBN (str): The ISBN of the recommended book.
    successful (bool): Whether the recommendation was successful or not.

    Returns:
    bool: True if the recommendation log was successfully added, False otherwise.
    """
    try:
        # Open connection to the database
        db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        logging.info("Database connection opened.")
        
        # Insert the recommendation log into the history table
        db.insert_records("history", [{"description": description, "recommendation_ISBN": recommendation_ISBN, "successful": successful}])
    
        return True
    except Exception as e:
        print(e)
        return False