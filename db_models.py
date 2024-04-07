import psycopg2
import pandas as pd
import numpy as np
from kitab.db.sql_interactions import SqlHandler

from kitab.db.get_data import get_full_data
user='yevamanukyan'
password='password'
host='localhost'
port='5432'
database = "book_rec"
try:
    
    # Getting the full data

    data = get_full_data()
    data["genre"].fillna("", inplace=True)
    data.dropna()
    data.drop(columns=["bookformat", "img", "isbn13", "link", "pages", "rating", "reviews", "totalratings", "embedding"])
    data.dropna(subset = ["isbn", "desc"], inplace=True)

    np.random.seed(42)
    data["available"] = np.random.random(len(data)) < 0.3

    book_table = data[["isbn", "title", "desc", "embedding", "available"]].rename(columns={"isbn":"ISBN", "desc":"description"})


    def split_and_filter(cell):
        if cell:
            return cell.split(",")
        else:
            return []

    authors = data["author"].apply(lambda x: split_and_filter(x))
    data["author"] = authors
    unique_authors = authors.explode().unique()
    author_table = pd.DataFrame({"author_id": range(len(unique_authors)), "full_name": unique_authors})

    book_author = data.explode("author")[["author", "isbn"]]
    book_author = pd.merge(book_author, author_table, how='left', left_on='author', right_on='full_name')[["isbn", "author_id"]]
    book_author.rename(columns={"isbn":"ISBN"}, inplace=True)
    book_author.drop_duplicates(inplace=True)
    book_author.reset_index(drop=True, inplace=True)

    genres = data["genre"].apply(lambda x: split_and_filter(x))
    data["genre"] = genres
    unique_genres = genres.explode().unique()
    genre_table = pd.DataFrame({"genre_id": range(len(unique_genres)), "genre": unique_genres})

    book_genre = data.explode("genre")[["genre", "isbn"]]
    book_genre = pd.merge(book_genre, genre_table, how='left', left_on='genre', right_on='genre')[["isbn", "genre_id"]]
    book_genre.rename(columns={"isbn":"ISBN"}, inplace=True)
    book_genre.drop_duplicates(inplace=True)
    book_genre.reset_index(drop=True, inplace=True)

    # Inserting Data

    # Book table
    sql_handler_book = SqlHandler(database, 'book', user=user, password=password, host = host, port = port)
    sql_handler_book.truncate_table()
    sql_handler_book.insert_many(book_table)
    sql_handler_book.close_cnxn()

    # Author table
    sql_handler_author = SqlHandler(database, 'author', user=user, password=password, host = host, port = port)
    sql_handler_author.truncate_table()
    sql_handler_author.insert_many(author_table)
    sql_handler_author.close_cnxn()

    # Genre table
    sql_handler_genre = SqlHandler(database, 'genre', user=user, password=password, host = host, port = port)
    sql_handler_genre.truncate_table()
    sql_handler_genre.insert_many(genre_table)
    sql_handler_genre.close_cnxn()

    # BookAuthor table
    sql_handler_bookauthor = SqlHandler(database, 'bookauthor', user=user, password=password, host = host, port = port)
    sql_handler_bookauthor.truncate_table()
    sql_handler_bookauthor.insert_many(book_author)
    sql_handler_bookauthor.close_cnxn()

    # BookGenre table
    sql_handler_bookgenre = SqlHandler(database, 'bookgenre', user=user, password=password, host = host, port = port)
    sql_handler_bookgenre.truncate_table()
    sql_handler_bookgenre.insert_many(book_genre)
    sql_handler_bookgenre.close_cnxn()



except psycopg2.Error as e:
    print("Error: Unable to connect to the PostgreSQL server.")
    print(e)
