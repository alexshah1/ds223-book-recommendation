import sqlite3
import logging 
import pandas as pd
import numpy as np
import os
from logger.logger import CustomFormatter

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class SqlHandler:

    def __init__(self, dbname:str,table_name:str) -> None:
        self.cnxn=sqlite3.connect(f'{dbname}.db')
        self.cursor=self.cnxn.cursor()
        self.dbname=dbname
        self.table_name=table_name

    def close_cnxn(self)->None:

        logger.info('commiting the changes')
        self.cursor.close()
        self.cnxn.close()
        logger.info('the connection has been closed')

    def insert_one()->None:
        pass

    def get_table_columns(self)->list:
        self.cursor.execute(f"PRAGMA table_info({self.table_name});")
        columns = self.cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        logger.info(f'the list of columns: {column_names}')
        # self.cursor.close()

        return column_names
    
    def truncate_table(self)->None:
        
        query=f"DROP TABLE IF EXISTS {self.table_name};"
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

    def insert_many(self, df:pd.DataFrame) -> str:
        
        df=df.replace(np.nan, None) # for handling NULLS
        df.rename(columns=lambda x: x.lower(), inplace=True)
        columns = list(df.columns)
        logger.info(f'BEFORE the column intersection: {columns}')
        sql_column_names = [i.lower() for i in self.get_table_columns()]
        columns = list(set(columns) & set(sql_column_names))
        logger.info(f'AFTER the column intersection: {columns}')
        ncolumns=list(len(columns)*'?')
        data_to_insert=df.loc[:,columns]
    
        values=[tuple(i) for i in data_to_insert.values]
        logger.info(f'the shape of the table which is going to be imported {data_to_insert.shape}')
        # if 'geometry' in columns: #! This block is usefull in case of geometry/geography data types
        #     df['geometry'] = df['geometry'].apply(lambda geom: dumps(geom))
        #     ncolumns[columns.index('geometry')]= 'geography::STGeomFromText(?, 4326)'
        
        if len(columns)>1:
            cols,params =', '.join(columns), ', '.join(ncolumns)
        else:
            cols,params =columns[0],ncolumns[0]
            
        logger.info(f'insert structure: colnames: {cols} params: {params}')
        logger.info(values[0])
        query=f"""INSERT INTO  {self.table_name} ({cols}) VALUES ({params});"""
        
        logger.info(f'QUERY: {query}')

        self.cursor.executemany(query, values)
        try:
            for i in self.cursor.messages:
                logger.info(i)
        except:
            pass


        self.cnxn.commit()
      
        
        logger.warning('the data is loaded')

    

    def from_sql_to_pandas(self, chunksize:int, id_value:str) -> pd.DataFrame:
        """

        """
        
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
        
        
    def calculate_similarity(self, ISBN: str, threshold: float = 0.5) -> pd.DataFrame:
        """
        Calculate similarity scores between the provided query ISBN and embeddings in the database.

        Parameters:
            ISBN (str): The ISBN of the query book.
            threshold (float): The minimum similarity threshold for results.

        Returns:
            pd.DataFrame: DataFrame containing book IDs and similarity scores.
        """
        # Retrieve query embedding from the database
        query_embedding = self.get_book_embedding_by_ISBN(ISBN)

        # Retrieve book embeddings from the database
        book_embeddings = self.get_book_embeddings()

        # Calculate similarity scores
        similarity_scores = []
        for idx, row in book_embeddings.iterrows():
            ISBN = row['ISBN']
            embedding = np.array(row['embedding'])
            # Calculate cosine similarity between query embedding and book embedding
            similarity_score = self.cosine_similarity(query_embedding, embedding)
            if similarity_score >= threshold:
                similarity_scores.append({'ISBN': ISBN, 'similarity_score': similarity_score})

        return pd.DataFrame(similarity_scores)


    def cosine_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate the cosine similarity between two vectors.

        Parameters:
            vector1 (np.ndarray): First vector.
            vector2 (np.ndarray): Second vector.

        Returns:
            float: Cosine similarity score between -1 and 1.
        """
        dot_product = np.dot(vector1, vector2)
        norm_vector1 = np.linalg.norm(vector1)
        norm_vector2 = np.linalg.norm(vector2)
        return dot_product / (norm_vector1 * norm_vector2)

