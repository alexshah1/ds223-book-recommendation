# Kitab - Book Recommendation System

[![PyPI version](https://badge.fury.io/py/kitab.svg)](https://badge.fury.io/py/kitab)

![Books](https://raw.githubusercontent.com/alexshah1/ds223-book-recommendation/main/docs/src/books.png "Books")

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

To start using the package functionalities, we need to load the data first. The data can be provided as a CSV file, which should include the following columns:

<br>
<center>

| Column Name | Data Type | Description                  |
|-------------|-----------|------------------------------|
| isbn        | str       | the ISBN of the book         |
| title       | str       | the title of the book        |
| description | str       | the description of the book  |
| author      | list[str] | the author(s) of the book    |
| genre       | list[str] | the genre(s) of the book     |
| available   | bool      | the availability of the book |

</center>
<br>

<i>Note: The table names might be different than the ones mentioned above. In that case, an additional parameter should be provided to specify the column names (`column_names` in `process_data()`).</i>

Before loading the data we need to process it. The `process_data()` function will process the data and generate the embeddings (this might take a while). It will split the data into parts, generate embeddings, store them in a specified folder. The folder will have numbered CSVs with the processed data and PKLs with the embeddings.

```{python}
from kitab.utils import process_data

filepath = "data.csv"
destination_folder = "data"

process_data(filepath, destination_folder)
```

Then we need to load the data into the database. For this, we need to provide the following database connection details in the `.env`:

<br>
<center>

| Parameter   | Description |
|-------------|-------------|
| DB_USER     | str         |
| DB_PASSWORD | str         |
| DB_HOST     | str         |
| DB_PORT     | str or int  |
| DB_NAME     | str         |

</center>
<br>

After that, we can load the data into the database using the `load_data()` function.

```{python}
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from kitab.db.get_data import load_data

load_data(destination_folder)
```

Now, we're ready to use the package functionalities. We can use the `recommend_books()` function to get recommendations for a book. The function takes the ISBN of the book and the number of recommendations you want to get.

```{python}
from kitab.recommendation_model.models import recommend_books

description = "In this thrilling detective tale, a group of childhood friends accidentally stumble upon an ancient artifact hidden in their clubhouse. Little do they know, their discovery thrusts them into a dangerous conspiracy spanning centuries. As they uncover clues, they race against time to prevent a cataclysmic event that could reshape the world. Join them on a heart-pounding journey through shadows and secrets in this gripping mystery."

recommend_books(description, n=5)
```

We can get a recommendation for a book using its ISBN or title as well.

```{python}
from kitab.recommendation_model.models import recommend_books_by_ISBN

recommend_books_by_ISBN(ISBN="1442942355", n=5)
```

```{python}
from kitab.recommendation_model.models import recommend_books_by_title

recommend_books_by_title(title="The Ghostly Rental", n=5)
```

Find full documentation [here](https://alexshah1.github.io/ds223-book-recommendation/).

© 2024 Team 8, DS 223 Marketing Analytics, AUA