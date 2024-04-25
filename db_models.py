import psycopg2
import pandas as pd
import numpy as np
from kitab.db.sql_interactions import SqlHandler
from kitab.db.db_info import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, COMMANDS
from kitab.db.get_data import get_full_data

try:
    # Getting the full data
    data = get_full_data()
    
    data.fillna({"genre": ""}, inplace=True)
    data.drop(columns=["bookformat", "img", "isbn13", "link", "pages", "rating", "reviews", "totalratings", "embedding"])
    data.dropna(subset = ["isbn", "desc"], inplace=True)

    np.random.seed(42)
    data["available"] = np.random.random(len(data)) < 0.3

    book_table = data[["isbn", "title", "desc", "embedding", "available"]].rename(columns={"isbn":"ISBN", "desc":"description"})


    def split_and_filter(cell):
        if cell:
            genres = cell.split(",")
            return [g.strip() for g in genres if g]
        else:
            return []

    authors = data["author"].apply(lambda x: split_and_filter(x))
    data["author"] = authors
    unique_authors = authors.explode().dropna().unique()
    author_table = pd.DataFrame({"author_id": range(1, len(unique_authors)+1), "full_name": unique_authors})

    books_with_authors = data[data['author'].map(lambda d: len(d)) > 0]
    book_author = books_with_authors.explode("author")[["author", "isbn"]]
    book_author = pd.merge(book_author, author_table, how='left', left_on='author', right_on='full_name')[["isbn", "author_id"]]
    book_author.rename(columns={"isbn":"ISBN"}, inplace=True)
    book_author.drop_duplicates(inplace=True)
    book_author.reset_index(drop=True, inplace=True)
    book_author["author_id"] = book_author["author_id"].astype(int)

    genres = data["genre"].apply(lambda x: split_and_filter(x))
    data["genre"] = genres
    unique_genres = genres.explode().dropna().unique()
    genre_table = pd.DataFrame({"genre_id": range(1, len(unique_genres)+1), "genre": unique_genres})

    books_with_genres = data[data['genre'].map(lambda d: len(d)) > 0]
    book_genre = books_with_genres.explode("genre")[["genre", "isbn"]]
    book_genre["genre"] = book_genre["genre"].str.strip()
    book_genre = pd.merge(book_genre, genre_table, how='left', left_on='genre', right_on='genre')[["isbn", "genre_id"]]
    book_genre.rename(columns={"isbn":"ISBN"}, inplace=True)
    book_genre.drop_duplicates(inplace=True)
    book_genre.reset_index(drop=True, inplace=True)
    book_genre["genre_id"] = book_genre["genre_id"].astype(int)

    # Establish connection with the database
    sql_handler = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

    # Create tables in the DB
    for command in COMMANDS:
        sql_handler.cursor.execute(command)

    # Inserting data
    # Book table
    sql_handler.insert_many(book_table, "book")

    # Author table
    sql_handler.insert_many(author_table, "author")

    # Genre table
    sql_handler.insert_many(genre_table, "genre")

    # BookAuthor table
    sql_handler.insert_many(book_author, "bookauthor")

    # BookGenre table
    sql_handler.insert_many(book_genre, "bookgenre")
    
    # Close the connection
    sql_handler.close_cnxn()


except psycopg2.Error as e:
    print("Error: Unable to connect to the PostgreSQL server.")
#     print(e)
