import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Get DB credentials from the environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

COMMANDS = (
    "CREATE EXTENSION IF NOT EXISTS vector;"

    "DROP TABLE IF EXISTS BookAuthor;",
        
    "DROP TABLE IF EXISTS Author;",
        
    "DROP TABLE IF EXISTS BookGenre;",
        
    "DROP TABLE IF EXISTS Genre;",
        
    "DROP TABLE IF EXISTS History;",
        
    "DROP TABLE IF EXISTS Book;",
        
    """CREATE TABLE Book (
        ISBN VARCHAR(20) PRIMARY KEY,
        title VARCHAR(2000),
        description VARCHAR(20000),
        embedding VECTOR(384), 
        available BOOLEAN
    );""",
        
    """CREATE TABLE Author (
        author_id SERIAL PRIMARY KEY,
        full_name VARCHAR(200)
    );""",

    """CREATE TABLE Genre (
        genre_id SERIAL PRIMARY KEY,
        genre VARCHAR(100)
    );""",

    """CREATE TABLE BookAuthor (
        ISBN VARCHAR(20),
        author_id SERIAL,
        PRIMARY KEY (ISBN, author_id),
        FOREIGN KEY (author_id) REFERENCES Author(author_id),
        FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON UPDATE CASCADE ON DELETE CASCADE
    );""",

    """CREATE TABLE BookGenre (
        ISBN VARCHAR(20),
        genre_id SERIAL,
        PRIMARY KEY (ISBN, genre_id),
        FOREIGN KEY (genre_id) REFERENCES Genre(genre_id),
        FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON UPDATE CASCADE ON DELETE CASCADE
    );""",
 
    """CREATE TABLE History (
        log_id INTEGER PRIMARY KEY,
        description VARCHAR(20000),
        recommendation_ISBN VARCHAR(20),
        successful BOOLEAN,
        datetime TIMESTAMP,
        FOREIGN KEY (recommendation_ISBN) REFERENCES Book(ISBN) ON UPDATE CASCADE ON DELETE CASCADE
    );"""
)