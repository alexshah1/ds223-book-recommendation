import pickle
import numpy as np
import pandas as pd
from glob import glob
from .db_info import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, COMMANDS, REQUIRED_COLUMNS
from .sql_interactions import SqlHandler
import psycopg2
import logging
from ..logger.logger import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)



def get_full_data(folder_path: str = "data"):
    """
    Retrieves and combines data from multiple CSV files and corresponding pickle files.
    
    Parameters:
    folder_path (str): The path to the directory containing the CSV and pickle files.
    
    Returns:
    pandas.DataFrame: A DataFrame containing the combined data with an additional 'embedding' column.
    """
    data_paths = sorted(glob(f"{folder_path}/*.csv"))
    emb_paths = sorted(glob(f"{folder_path}/*.pkl"))
    
    if len(data_paths) == 0:
        raise Exception("No CSV files found in the specified folder.")
    elif len(emb_paths) == 0:
        raise Exception("No PKL files found in the specified folder.")
    elif len(data_paths) != len(emb_paths):
        raise Exception("The number of CSV and PKL files do not match.")
    
    logger.info("Data and embeddings found successfully.")
    
    datas = [pd.read_csv(data_path) for data_path in data_paths]
    embs = []
    
    for emb_path in emb_paths:
        with open(emb_path, "rb") as f:
            emb = pickle.load(f)
        embs.append(emb)
     
    df = pd.concat(datas).reset_index(drop=True)
    df["embedding"] = np.concatenate(embs).tolist()
    
    logger.info("Data and embeddings combined successfully.")
 
    return df


def load_data(folder_path: str = "data"):
    """
    Load data from a specified folder path and insert it into the database.

    Parameters:
    - folder_path (str): The path to the folder containing the data files. Default is "data".

    Returns:
    None
    """
    try:
        # Getting the full data
        data = get_full_data(folder_path)
        
        data.fillna({"genre": ""}, inplace=True)
        data = data[REQUIRED_COLUMNS + ["embedding", "available"]]
        
        data.dropna(subset = ["isbn", "description"], inplace=True)

        book_table = data[["isbn", "title", "description", "embedding", "available"]]
        
        logger.info("Data loaded successfully.")

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
        
        logger.info("Authors extracted successfully.")

        books_with_authors = data[data['author'].map(lambda d: len(d)) > 0]
        book_author = books_with_authors.explode("author")[["author", "isbn"]]
        book_author = pd.merge(book_author, author_table, how='left', left_on='author', right_on='full_name')[["isbn", "author_id"]]
        # book_author.rename(columns={"isbn":"ISBN"}, inplace=True)
        book_author.drop_duplicates(inplace=True)
        book_author.reset_index(drop=True, inplace=True)
        book_author["author_id"] = book_author["author_id"].astype(int)
        
        logger.info("Book-Author mapping created successfully.")

        genres = data["genre"].apply(lambda x: split_and_filter(x))
        data["genre"] = genres
        unique_genres = genres.explode().dropna().unique()
        genre_table = pd.DataFrame({"genre_id": range(1, len(unique_genres)+1), "genre": unique_genres})
        
        logger.info("Genres extracted successfully.")

        books_with_genres = data[data['genre'].map(lambda d: len(d)) > 0]
        book_genre = books_with_genres.explode("genre")[["genre", "isbn"]]
        book_genre["genre"] = book_genre["genre"].str.strip()
        book_genre = pd.merge(book_genre, genre_table, how='left', left_on='genre', right_on='genre')[["isbn", "genre_id"]]
        # book_genre.rename(columns={"isbn":"ISBN"}, inplace=True)
        book_genre.drop_duplicates(inplace=True)
        book_genre.reset_index(drop=True, inplace=True)
        book_genre["genre_id"] = book_genre["genre_id"].astype(int)
        
        logger.info("Book-Genre mapping created successfully.")

        # Establish connection with the database
        sql_handler = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

        # Create tables in the DB
        for command in COMMANDS:
            sql_handler.cursor.execute(command)
            
        logger.info("Tables created successfully.")

        # Inserting data
        # Book table
        sql_handler.insert_many(book_table, "book")
        
        logger.info("Book data inserted successfully.")

        # Author table
        sql_handler.insert_many(author_table, "author")
        
        logger.info("Author data inserted successfully.")

        # Genre table
        sql_handler.insert_many(genre_table, "genre")
        
        logger.info("Genre data inserted successfully.")

        # BookAuthor table
        sql_handler.insert_many(book_author, "bookauthor")
        
        logger.info("Book-Author mapping inserted successfully.")

        # BookGenre table
        sql_handler.insert_many(book_genre, "bookgenre")
        
        logger.info("Book-Genre mapping inserted successfully.")
        
        # Close the connection
        sql_handler.close_cnxn()

    except psycopg2.Error as e:
        print("Error: Unable to connect to the PostgreSQL server.")