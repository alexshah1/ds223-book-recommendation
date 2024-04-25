"""
This module contains the functions for interacting with the SQL database.
"""
import psycopg2
from pgvector.psycopg2 import register_vector
import logging
import pandas as pd
import numpy as np

from ..logger.logger import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class SqlHandler:

    def __init__(self, dbname: str, user: str, password: str, host: str, port: str) -> None:
        # Check credentials
        print([dbname, user, password, host, port])
        if any(not cred for cred in [dbname, user, password, host, port]):
            raise Exception("Some database credentials were not passed. Please fill in the database credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) in db_info.py.")
        
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()
        register_vector(self.connection)
    
    def close_cnxn(self) -> None:
        """
        Close the connection to the database.
        
        Returns:
        None
        """
        logger.info('Committing the changes.')
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        logger.info('The connection has been closed.')


    def get_table_columns(self, table_name: str) -> list:
        """
        Retrieves the columns of a table in the database.
        
        Parameters:
        table_name (str): The name of the table whose columns are to be retrieved.
        
        Returns:
        list: A list of column names in the table.
        """
        try:
            self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
            columns = self.cursor.fetchall()
            column_names = [col[0] for col in columns]
            logger.info(f'Retrieved columns for table {table_name}: {column_names}')
            return column_names
        except Exception as e:
            logger.error(f'Error occurred while retrieving columns for table {table_name}: {e}')
            return []
    
    
    def execute_commands(self, commands: list) -> None:
        """
        Executes a list of commands in the database.
        
        Parameters:
        commands (list): A list of SQL commands to be executed.
        
        Returns:
        None
        """
        for command in commands:
            self.cursor.execute(command)
        self.connection.commit()
        logger.info('Commands executed successfully.')


    def insert_many(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Inserts data from a DataFrame into a table in the database.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the data to be inserted.
        table_name (str): The name of the table to be dropped.

        Returns:
        None
        """
        try:
            df = df.replace(np.nan, None)  # for handling NULLS
            df.rename(columns=lambda x: x.lower(), inplace=True)
            columns = list(df.columns)
            logger.info(f'Columns before intersection: {columns}')
            sql_column_names = [i.lower() for i in self.get_table_columns(table_name)]
            columns = list(set(columns) & set(sql_column_names))
            logger.info(f'Columns after intersection: {columns}')
            data_to_insert = df.loc[:, columns]
            values = []
            for row in data_to_insert.itertuples(index=False):
                values.append(tuple(row))
            logger.info(f'Shape of the table to be imported: {data_to_insert.shape}')
            ncolumns = len(columns)
            params = ','.join(['%s'] * ncolumns)
            if len(columns) > 1:
                cols = ', '.join(columns)
            else:
                cols = columns[0]
            logger.info(f'Insert structure: Columns: {cols}, Parameters: {params}')
            query = f"INSERT INTO {table_name} ({cols}) VALUES ({params});"
            logger.info(f'Query: {query}')
            self.cursor.executemany(query, values)
            self.connection.commit()
            logger.warning('Data loaded successfully.')
        except Exception as e:
            logger.error(f'Error occurred while inserting data into {table_name}: {e}')


    def truncate_table(self, table_name: str) -> None:
        """
        Truncates a table from the database.

        Parameters:
        table_name (str): The name of the table to be truncated.

        Returns:
        None
        """
        query = f""" TRUNCATE TABLE {table_name} CASCADE; """   #if exists
        self.cursor.execute(query)
        logging.info(f'the {table_name} is truncated')
        # self.cursor.close()


    def drop_table(self, table_name: str) -> None:
        """
        Drops a table from the database if it exists.

        Parameters:
        table_name (str): The name of the table to be dropped.

        Returns:
        None
        """
        query = f"DROP TABLE IF EXISTS {table_name};"
        logging.info(query)

        self.cursor.execute(query)

        self.close_cnxn.commit()

        logging.info(f"table '{table_name}' deleted.")
        logger.debug('using drop table function')


    # def from_sql_to_pandas(self, chunksize:int, id_value:str, table_name: str) -> pd.DataFrame:
        
    #     offset=0
    #     dfs=[]

    #     while True:
    #         query=f"""
    #         SELECT * FROM {table_name}
    #             ORDER BY {id_value}
    #             OFFSET  {offset}  ROWS
    #             FETCH NEXT {chunksize} ROWS ONLY  
    #         """

    #         data = pd.read_sql_query(query,self.close_cnxn) 
    #         logger.info(f'the shape of the chunk: {data.shape}')
    #         dfs.append(data)
    #         offset += chunksize
    #         if len(dfs[-1]) < chunksize:
    #             logger.warning('loading the data from SQL is finished')
    #             logger.debug('connection is closed')
    #             break
    #     df = pd.concat(dfs)

    #     return df
        
    def insert_records(self, table_name: str, values_list: list[dict]) -> None:
        """
        Insert one or more records into the database table.

        Parameters:
            values_list (List[Dict]): A list of dictionaries containing column names as keys and their values as values.

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

        logger.info(f"{len(values_list)} records inserted successfully.")

    def update_records(self, table_name: str, update_values: dict, condition: dict) -> None:
        """
        Update records in the database table based on a given condition.

        Parameters:
            table_name (str): The name of the table to update records in.
            condition (dict): A dictionary representing the condition for selecting records to update.
            update_values (dict): A dictionary containing column names as keys and their updated values as values.

        Returns:
            None
        """
        if not condition:
            logger.warning("No condition provided for updating records.")
            return

        if not update_values:
            logger.warning("No values provided for update.")
            return

        set_clause = ', '.join([f"{column} = %s" for column in update_values.keys()])
        condition_clause = ' AND '.join([f"{column} = %s" for column in condition.keys()])

        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_clause};"
        values = list(update_values.values()) + list(condition.values())

        self.cursor.execute(query, tuple(values))
        self.connection.commit()

        logger.info("Records updated successfully.")
        
    def remove_records(self, table_name: str, conditions_list: list[dict]) -> None:
        """
        Remove records from the database table based on multiple conditions.

        Parameters:
            table_name (str): The name of the table to remove records from.
            conditions_list (list[dict]): A list of dictionaries representing conditions for selecting records to remove.
                The conditions inside each dictionary are concatenated using AND, and the dictionaries inside the list are concatenated using OR.

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

        logger.info("Records removed successfully.")

    def get_table(self, table_name: str, conditions: dict = None) -> pd.DataFrame:
        """
        Retrieve data from the database table.

        Parameters:
            table_name (str): The name of the table to retrieve data from.
            conditions (dict, optional): A dictionary representing the conditions to filter records. Defaults to None.

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
        
        return data

    # def get_book_embeddings(self, table_name: str) -> pd.DataFrame:
    #     """
    #     Retrieve book embeddings from the database.

    #     Returns:
    #         pd.DataFrame: DataFrame containing book IDs and embeddings.
    #     """
    #     query = f"SELECT ISBN, embedding FROM {table_name};"
    #     return pd.read_sql_query(query, self.close_cnxn)
    
    # def get_book_embedding_by_ISBN(self, ISBN: str, table_name: str) -> np.ndarray:
    #     """
    #     Retrieve book embedding from the database based on ISBN.

    #     Parameters:
    #         ISBN (str): The ISBN of the book.

    #     Returns:
    #         np.ndarray: The embedding of the book.
    #     """
    #     query = f"SELECT embedding FROM {table_name} WHERE ISBN = ?;"
    #     self.cursor.execute(query, (ISBN,))
    #     row = self.cursor.fetchone()
    #     if row:
    #         return np.array(row[0])
    #     else:
    #         raise ValueError(f"No embedding found for book with ISBN: {ISBN}")
        