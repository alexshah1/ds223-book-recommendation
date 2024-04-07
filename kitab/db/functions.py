import pandas as pd
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

# def update_book(book: dict) -> None:
#     """
#     Update a book record in the database.

#     Parameters:
#         ISBN (str): The ISBN of the book to be updated.
#         new_ISBN (str): The new ISBN for the book (optional).
#         new_title (str): The new title for the book (optional).
#         new_desc (str): The new description for the book (optional).
#         new_available (bool): The new availability status for the book (optional).

#     Returns:
#         None
#     """
#     if book["ISBN"] is None:
#         book.pop("ISBN")

#     if book["title"] is None:
#         book.pop("title")

#     if book["description"] is None:
#         book.pop("description")

#     if book["available"] is None:
#         book.pop("available")

#     if book["description"] is not None:
#         new_embedding = self.get_embedding(book["description"])
#         book["embedding"] = new_embedding

#     set_clause = ', '.join([f"{col} = %s" for col in update_values.keys()])

#     # Values for the SQL query
#     values = tuple(book.values())

#     # Executing SQL query to update the book record in the database
#     try:
#         query = f"UPDATE {self.table_name} SET {set_clause} WHERE ISBN = %s;"
#         self.cursor.execute(query, values + (ISBN,))
#         self.connection.commit()
#         logger.info(f"Book with ISBN '{ISBN}' updated successfully.")
#     except Exception as e:
#         logger.error(f"Error occurred while updating book with ISBN '{ISBN}': {e}")


def get_table_from_db(table_name: str) -> pd.DataFrame:
    # Open connection to the database
    # Retrieve the table from the database
    # Return the table
    pass

