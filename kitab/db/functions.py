import pandas as pd

def get_book_by_ISBN(ISBN: str):
    # Open connection to the database
    # Retrieve the book with the given ISBN
    # If no book found, return None
    # If book found, join with author and genres tables to get the author(s) and genres
    # Return the book
    pass

def add_book_db(book: dict):
    # Open connection to the database
    # Add book to the database
    # Add author(s) to the author table if doesn't exist
    # Add genres to the genres table if doesn't exist
    # Add to the bookauthor and bookgenre tables
    # Return true
    pass

def update_book_db(book: dict):
    # Open connection to the database
    # Update the book table, if there's anything to update
    # Update the bookauthor and bookgenre table if there's anything to update
    pass

def get_table_from_db(table_name: str) -> pd.DataFrame:
    # Open connection to the database
    # Retrieve the table from the database
    # Return the table
    pass