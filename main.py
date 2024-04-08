from kitab.db.functions import *
from kitab.db.db_info import user, port, password, host, database
# isbn = "087584717X"

add_book_db({"ISBN": "test_isbn", "title": "test_title", "description": "test_description", "available": True, "authors": ["test_author", "Agatha Christie"], "genres": ["test_genre", "Fiction"]})