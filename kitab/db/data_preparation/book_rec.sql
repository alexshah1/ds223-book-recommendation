CREATE TABLE Book (
    ISBN VARCHAR(2000) PRIMARY KEY,
    title VARCHAR(2000),
    description VARCHAR(8000),  --maybe can make this larger
    embedding VECTOR(384), 
    available BOOLEAN
);

CREATE TABLE BookAuthor (
    ISBN INTEGER,
    author_id INTEGER,
    PRIMARY KEY (ISBN, author_id),
    FOREIGN KEY (author_id) REFERENCES Author(author_id),
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN)
);

CREATE TABLE History (
    log_id INTEGER PRIMARY KEY,
    description VARCHAR(8000),
    recommendation_ISBN VARCHAR(2000),
    successful BOOLEAN,
    datetime TIMESTAMP,
    FOREIGN KEY (recommendation_ISBN) REFERENCES Book(ISBN)
);

CREATE TABLE Genre (
    genre_id INTEGER PRIMARY KEY,
    genre VARCHAR(100)
);

CREATE TABLE BookGenre (
    ISBN VARCHAR(2000),
    genre_id INTEGER,
    PRIMARY KEY (ISBN, genre_id),
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN),
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
);

CREATE TABLE Author (
    author_id INTEGER PRIMARY KEY,
    full_name VARCHAR(200)
);
