import psycopg2
import logging
import pandas as pd
import numpy as np

from ..logger import CustomFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class SqlHandler:

    def __init__(self, dbname: str, table_name: str) -> None:
        self.connection = psycopg2.connect(dbname=dbname, user='username', password='password', host='host_name', port='port')
        self.cursor = self.connection.cursor()
        self.table_name = table_name

    def close_cnxn(self) -> None:
        logger.info('Committing the changes.')
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        logger.info('The connection has been closed.')

    def get_table_columns(self) -> list:
        try:
            self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{self.table_name}';")
            columns = self.cursor.fetchall()
            column_names = [col[0] for col in columns]
            logger.info(f'Retrieved columns for table {self.table_name}: {column_names}')
            return column_names
        except Exception as e:
            logger.error(f'Error occurred while retrieving columns for table {self.table_name}: {e}')
            return []

    def insert_many(self, df: pd.DataFrame) -> None:
        try:
            df = df.replace(np.nan, None)  # for handling NULLS
            df.rename(columns=lambda x: x.lower(), inplace=True)
            columns = list(df.columns)
            logger.info(f'Columns before intersection: {columns}')
            sql_column_names = [i.lower() for i in self.get_table_columns()]
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
            query = f"INSERT INTO {self.table_name} ({cols}) VALUES ({params});"
            logger.info(f'Query: {query}')
            self.cursor.executemany(query, values)
            self.connection.commit()
            logger.warning('Data loaded successfully.')
        except Exception as e:
            logger.error(f'Error occurred while inserting data into {self.table_name}: {e}')


    def truncate_table(self)->None:
        
        query=f"TRUNCATE TABLE IF EXISTS {self.table_name};"
        self.cursor.execute(query)
        logging.info(f'the {self.table_name} is truncated')
        # self.cursor.close()


    def drop_table(self):
        
        query = f"DROP TABLE IF EXISTS {self.table_name};"
        logging.info(query)

        self.cursor.execute(query)

        self.cnxn.commit()

        logging.info(f"table '{self.table_name}' deleted.")
        logger.debug('using drop table function')


    def from_sql_to_pandas(self, chunksize:int, id_value:str) -> pd.DataFrame:
        
        offset=0
        dfs=[]
       
        
        while True:
            query=f"""
            SELECT * FROM {self.table_name}
                ORDER BY {id_value}
                OFFSET  {offset}  ROWS
                FETCH NEXT {chunksize} ROWS ONLY  
            """
            data = pd.read_sql_query(query,self.cnxn) 
            logger.info(f'the shape of the chunk: {data.shape}')
            dfs.append(data)
            offset += chunksize
            if len(dfs[-1]) < chunksize:
                logger.warning('loading the data from SQL is finished')
                logger.debug('connection is closed')
                break
        df = pd.concat(dfs)

        return df


    def update_table(self, condition: str, update_values: dict) -> None:
        """
        Update records in the database table based on the specified condition.

        Parameters:
            condition (str): The SQL condition to filter records to be updated.
            update_values (dict): A dictionary containing column names as keys and their updated values as values.

        Returns:
            None
        """
        set_clause = ', '.join([f"{col} = ?" for col in update_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {condition};"
        
        values = tuple(update_values.values())

        self.cursor.execute(query, values)
        self.cnxn.commit()

        logger.info("Table updated successfully.")



    def get_book_embeddings(self) -> pd.DataFrame:
        """
        Retrieve book embeddings from the database.

        Returns:
            pd.DataFrame: DataFrame containing book IDs and embeddings.
        """
        query = f"SELECT ISBN, embedding FROM {self.table_name};"
        return pd.read_sql_query(query, self.cnxn)
    

    def get_book_embedding_by_ISBN(self, ISBN: str) -> np.ndarray:
        """
        Retrieve book embedding from the database based on ISBN.

        Parameters:
            ISBN (str): The ISBN of the book.

        Returns:
            np.ndarray: The embedding of the book.
        """
        query = f"SELECT embedding FROM {self.table_name} WHERE ISBN = ?;"
        self.cursor.execute(query, (ISBN,))
        row = self.cursor.fetchone()
        if row:
            return np.array(row[0])
        else:
            raise ValueError(f"No embedding found for book with ISBN: {ISBN}")
    