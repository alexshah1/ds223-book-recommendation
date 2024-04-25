# Database Schema

## Overview
Our system uses a PostgreSQL database to store information about books, authors, genres, and user interactions. Below is a detailed schema representation.

### Tables
- **Book**: Stores book  titles, descriptions, availability.
- **BookAuthor**: Stores ISBN key and auther ID key
- **Author**: Stores author full names and ID key.
- **BookGenre**: Stores genre IDs and ISBN.
- **Gnere**: Stores genre and ID.
- **History**: Stores ID,  description, reccomenadtion ISBN, datetime and success
