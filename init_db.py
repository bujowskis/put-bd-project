import pandas as pd
import numpy as np
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from cassandra import ConsistencyLevel


def main():
    cluster = Cluster(['c1', 'c2', 'c3'])
    session = cluster.connect()

    print('create and use keyspace')
    keyspace_name = 'bookkeeper'  # books?
    session.execute(
        f"CREATE KEYSPACE IF NOT EXISTS {keyspace_name} "
        f"WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}"
    )
    session.execute(f'USE {keyspace_name}')

    print('drop data if reinitializing')
    table_name = 'books'
    session.execute(f'DROP TABLE IF EXISTS {table_name}')

    print('initialize database')
    books_df = pd.read_csv('./dataset.csv')
    print(books_df.info())
    columns = list(books_df.columns)
    columns_types = list([
        # pandas/numpy data types need to be mapped into cassandra types
        'bigint' if dtype == 'int64' else
        'double' if dtype == 'float64' else
        'text'
        for dtype in books_df.dtypes.tolist()
    ])
    print('\tcreate table')
    session.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (" +
        ", ".join([f"{column} {dtype.upper()}" for column, dtype in zip(columns, columns_types)]) + ", " +
        "PRIMARY KEY (isbn));"
    )
    print('\tbatch insert data')
    batch_size, number_of_rows, number_of_columns = 64, len(books_df), len(columns)
    number_of_batches = int(np.ceil(number_of_rows / batch_size))
    for batch_idx in range(number_of_batches):
        batch_start_idx = batch_idx * batch_size
        batch_end_idx = min(batch_start_idx + batch_size, number_of_rows)
        batch_statement = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        for _, row in books_df.iloc[batch_start_idx:batch_end_idx].iterrows():
            batch_statement.add(
                f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({','.join(['%s'] * number_of_columns)})",
                row.tolist()
            )
        session.execute(batch_statement)

    print('\tdatabase initialized')
    session.shutdown()
    cluster.shutdown()


if __name__ == '__main__':
    main()
