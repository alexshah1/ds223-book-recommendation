# Kitab - Book Recommendation System

[![PyPI version](https://badge.fury.io/py/kitab.svg)](https://badge.fury.io/py/kitab)

![Books](docs/src/books.png "Books")

## Package Overview
The **Kitab** package aims to help bookstores with an easy-to-use recommendation system. When a customer requests a book that is currently unavailable, the system will utilize machine learning techniques to find similar books based on attributes such as genre, author, and book description. This will help bookstores enhance customer satisfaction and increase sales by offering relevant alternatives.

## Package Name
The package name is **Kitab**, which is the word for *book* in Arabic, Swahili, Urdu, Hindi and various Indian and Turkic languages.

## Contributors
The package was created as the final project of the DS 223 Marketing Analytics class at the American University of Armenia (AUA) during the Spring 2024 semester. The team members are:

- Alexander Shahramanyan
- Anna Charchyan
- Yeva Manukyan
- Lilith Asminian
- Maria Petrosyan

The instructor of the course is Professor Karen Hovhannisyan. He oversaw the project and provided guidance to the team throughout the semester.

## Installation

To install the package, run the following command:

```{bash}
pip install kitab
```

To upgrade the package, run the following command:

```{bash}
pip install kitab --upgrade
```

## Requirements

Currently, the package only supports PostgreSQL databases. You need to have a PostgreSQL database installed on your machine to use the package.

Additionally, since the package needs to store vectors, `pgvector` should be installed. To install it, follow the steps mentioned in the [pgvector GitHub repo](https://github.com/pgvector/pgvector).

All other requirements will be installed when the package is installed/updated using `pip`.

## Usage

To start using the package functionalities, you need to import the package in your Python script. Then you need to provide the book data, which should include the following columns:

- isbn (str) - the ISBN of the book,
- title (str) the title of the book, 
- description (str) the description of the book,
- author (list[str]) - the authors of the book,
- genre (list[str]) - the genres of the book,
- available (bool) - whether the book is available or not (optional; you can use random initialization of this column).

The `process_data()` function will process the data and generate the embeddings (this might take a while). It will split the data into parts, generate embeddings, store them in a specified folder. The folder will have numbered CSVs with the processed data and PKLs with the embeddings.

```{python}
from kitab.utils import process_data

filepath = "data.csv"
destination_folder = "data"

process_data(filepath, destination_folder)
```

Then you need to load these data into the database. For this, you need to provide the database connection details in your `.env` file as follows: 

```{bash}
DB_USER='' # Database username
DB_PASSWORD='' # Database password
DB_HOST='' # Database host
DB_PORT='' # Database port
DB_NAME='' # Database name
```

Then using the `load_data()` function, the data can be loaded into the database. The function gets the path of the folder which stores the data and the embeddings, combine these, and load them into the database.

```{python}
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from kitab.db.get_data import load_data

load_data(destination_folder)
```

Then you're ready to use the package functionalities. You can use the `recommend_books()` function to get recommendations for a book. The function takes the ISBN of the book and the number of recommendations you want to get.

```{python}
from kitab.recommmendation_model import recommend_books

description = "In this thrilling detective tale, a group of childhood friends accidentally stumble upon an ancient artifact hidden in their clubhouse. Little do they know, their discovery thrusts them into a dangerous conspiracy spanning centuries. As they uncover clues, they race against time to prevent a cataclysmic event that could reshape the world. Join them on a heart-pounding journey through shadows and secrets in this gripping mystery."

recommend_books(description, n=5)
```

Find full documentation [here](https://alexshah1.github.io/ds223-book-recommendation/).

© 2024 Team 8, DS 223 Marketing Analytics, AUA