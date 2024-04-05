import psycopg2

host = "localhost"          # Hostname or IP address of the PostgreSQL server
port = "5432"          # Port number of the PostgreSQL server (default is 5432)
database = "book_rec"  # Name of the database to connect to


# Establishing a connection to the PostgreSQL server
try:

    connection = psycopg2.connect(
        host=host,
        port=port,
    
        database=database

    )
    print("Successfully connected to the PostgreSQL server.")

    # Perform database operations here...

    # Closing the connection
    connection.close()
    print("Connection to the PostgreSQL server closed.")

except psycopg2.Error as e:
    print("Error: Unable to connect to the PostgreSQL server.")
    print(e)
