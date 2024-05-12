"""
This module contains the functions for interacting with the SQL database.
"""
import psycopg2
from pgvector.psycopg2 import register_vector
import pandas as pd
import numpy as np
import logging
from ..logger.logger import CustomFormatter

import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class SqlHandler:

    def __init__(self, dbname: str, user: str, password: str, host: str, port: str) -> None:
        # Check credentials
        if any(not cred for cred in [dbname, user, password, host, port]):
            raise Exception("Some database credentials were not passed. Please pas the database credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) as environment variables (in .env).")
        
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        register_vector(self.connection)
    
    def close_cnxn(self, verbose: bool = False) -> None:
        """
        Close the connection to the database.
        
        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> db.close_cnxn()
        
        Parameters:
            verbose (bool): Whether to print verbose output. Defaults to False.
        
        Returns:
            None
        """
        if verbose:
            logger.info('Committing the changes.')
            
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        
        if verbose:
            logger.info('The connection has been closed.')


    def get_table_columns(self, table_name: str, verbose: bool = False) -> list:
        """
        Retrieves the columns of a table in the database.
        
        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> db.get_table_columns("Book")

        Parameters:
            table_name (str): The name of the table whose columns are to be retrieved.
            verbose (bool): Whether to print verbose output. Defaults to False.
        
        Returns:
            list: A list of column names in the table.
        """
        try:
            self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
            columns = self.cursor.fetchall()
            column_names = [col[0] for col in columns]
            if verbose:
                logger.info(f'Retrieved columns for table {table_name}: {column_names}')
            return column_names
        except Exception as e:
            if verbose:
                logger.error(f'Error occurred while retrieving columns for table {table_name}: {e}')
            return []
    
    
    def execute_commands(self, commands: list, verbose: bool = False) -> None:
        """
        Executes a list of commands in the database.
        
        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> commands = [...]
            >>> db.execute_commands(commands)

        Parameters:
            commands (list): A list of SQL commands to be executed.
            verbose (bool): Whether to print verbose output. Defaults to False.
        
        Returns:
            None
        """
        for command in commands:
            self.cursor.execute(command)
            
        self.connection.commit()
        
        if verbose:
            logger.info('Commands executed successfully.')


    def insert_many(self, df: pd.DataFrame, table_name: str, verbose: bool = False) -> None:
        """
        Inserts data from a DataFrame into a table in the database.

        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> df = pd.DataFrame(...)
            >>> db.insert_many(df, "Book")

        Parameters:
            df (pd.DataFrame): The DataFrame containing the data to be inserted.
            table_name (str): The name of the table to be dropped.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            None
        """
        try:
            df = df.replace(np.nan, None)  # for handling NULLS
            df.rename(columns=lambda x: x.lower(), inplace=True)
            columns = list(df.columns)
            
            if verbose:
                logger.info(f'Columns before intersection: {columns}')
                
            sql_column_names = [i.lower() for i in self.get_table_columns(table_name)]
            columns = list(set(columns) & set(sql_column_names))
            
            if verbose:
                logger.info(f'Columns after intersection: {columns}')
                
            data_to_insert = df.loc[:, columns]
            values = []
            
            for row in data_to_insert.itertuples(index=False):
                values.append(tuple(row))
                
            if verbose:
                logger.info(f'Shape of the table to be imported: {data_to_insert.shape}')
                
            ncolumns = len(columns)
            params = ','.join(['%s'] * ncolumns)
            
            if len(columns) > 1:
                cols = ', '.join(columns)
            else:
                cols = columns[0]
                
            if verbose:
                logger.info(f'Insert structure: Columns: {cols}, Parameters: {params}')
                
            query = f"INSERT INTO {table_name} ({cols}) VALUES ({params});"
            
            if verbose:
                logger.info(f'Query: {query}')
                
            self.cursor.executemany(query, values)
            self.connection.commit()
            
            if verbose:
                logger.info('Data loaded successfully.')
        except Exception as e:
            logger.error(f'Error occurred while inserting data into {table_name}: {e}')


    def truncate_table(self, table_name: str, verbose: bool = False) -> None:
        """
        Truncates a table from the database.

        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> db.truncate_table("Book")

        Parameters:
            table_name (str): The name of the table to be truncated.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            None
        """
        query = f""" TRUNCATE TABLE {table_name} CASCADE; """   #if exists
        self.cursor.execute(query)
        
        if verbose:
            logger.info(f'the {table_name} is truncated')
            
        # self.cursor.close()


    def drop_table(self, table_name: str, verbose: bool = False) -> None:
        """
        Drops a table from the database if it exists.

        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> db.drop_table("Book")

        Parameters:
            table_name (str): The name of the table to be dropped.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            None
        """
        query = f"DROP TABLE IF EXISTS {table_name};"
        if verbose:
                logger.info(query)

        self.cursor.execute(query)

        self.close_cnxn.commit()

        if verbose:
            logger.info(f"Table '{table_name}' deleted.")

        
    def insert_records(self, table_name: str, values_list: list[dict], verbose: bool = False) -> None:
        """
        Insert one or more records into the database table.

        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> list_of_books = [...]
            >>> db.insert_records("Book", list_of_books)

        Parameters:
            values_list (List[Dict]): A list of dictionaries containing column names as keys and their values as values.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            None
        """
        if not values_list:
            logger.warning("No records to insert.")
            return            

        columns = ', '.join(values_list[0].keys())
        placeholders = '(' + ', '.join(['%s'] * len(values_list[0])) + ')'
        query = f"INSERT INTO {table_name} ({columns}) VALUES {placeholders};"        
        values = [tuple(value.values()) for value in values_list]

        self.cursor.executemany(query, values)
        self.connection.commit()

        if verbose:
            logger.info(f"{len(values_list)} records inserted successfully.")


    def update_records(self, table_name: str, updated_values: dict, condition: dict, verbose: bool = False) -> None:
        """
        Update records in the database table based on a given condition.

        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> updated_values = {...}
            >>> conditions = {...}
            >>> db.update_records("Book", updated_values, conditions)        

        Parameters:
            table_name (str): The name of the table to update records in.
            condition (dict): A dictionary representing the condition for selecting records to update.
            updated_values (dict): A dictionary containing column names as keys and their updated values as values.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            None
        """
        if not condition:
            logger.warning("No condition provided for updating records.")
            return

        if not updated_values:
            logger.warning("No values provided for update.")
            return

        set_clause = ', '.join([f"{column} = %s" for column in updated_values.keys()])
        condition_clause = ' AND '.join([f"{column} = %s" for column in condition.keys()])

        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_clause};"
        values = list(updated_values.values()) + list(condition.values())

        self.cursor.execute(query, tuple(values))
        self.connection.commit()

        if verbose:
            logger.info("Records updated successfully.")
        
    def remove_records(self, table_name: str, conditions_list: list[dict], verbose: bool = False) -> None:
        """
        Remove records from the database table based on multiple conditions.
        
        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> list_of_conditions = [...]
            >>> db.remove_records("Book", list_of_conditions)          

        Parameters:
            table_name (str): The name of the table to remove records from.
            conditions_list (list[dict]): A list of dictionaries representing conditions for selecting records to remove.
                The conditions inside each dictionary are concatenated using AND, and the dictionaries inside the list are concatenated using OR.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            None
        """
        if not conditions_list:
            logger.warning("No conditions provided for removing records.")
            return

        condition_clauses = []
        values = []

        for condition in conditions_list:
            condition_clause = ' AND '.join([f"{column} = %s" for column in condition.keys()])
            condition_clauses.append(f"({condition_clause})")
            values.extend(list(condition.values()))

        where_clause = ' OR '.join(condition_clauses)
        query = f"DELETE FROM {table_name} WHERE {where_clause};"

        self.cursor.execute(query, tuple(values))
        self.connection.commit()

        if verbose:
            logger.info("Records removed successfully.")

    def get_table(self, table_name: str, conditions: dict = None, verbose: bool = False) -> pd.DataFrame:
        """
        Retrieve data from the database table.

        Examples:
            >>> from kitab.db.sql_interactions import SqlHandler
            >>> from kitab.db.db_credentials import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
            >>> db = SqlHandler(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            >>> list_of_conditions = [...]
            >>> db.get_table("Book", list_of_conditions)          
        
        Parameters:
            table_name (str): The name of the table to retrieve data from.
            conditions (dict, optional): A dictionary representing the conditions to filter records. Defaults to None.
            verbose (bool): Whether to print verbose output. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing the retrieved data.
        """
        if conditions:
            condition_clauses = []
            values = []
            for column, value in conditions.items():
                if isinstance(value, list):
                    placeholders = ', '.join(['%s'] * len(value))
                    condition_clauses.append(f"{column} IN ({placeholders})")
                    values.extend(value)
                else:
                    condition_clauses.append(f"{column} = %s")
                    values.append(value)
            
            condition_clause = ' AND '.join(condition_clauses)
            query = f"SELECT * FROM {table_name} WHERE {condition_clause};"
            data = pd.read_sql(query, self.connection, params=values)
        else:
            query = f"SELECT * FROM {table_name};"
            data = pd.read_sql(query, self.connection)
        
        if verbose:
            logger.info("Table retrieved successfully.")
        
        return data