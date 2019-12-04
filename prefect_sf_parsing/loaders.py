from prefect import task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prefect_sf_parsing.models import Base
from typing import List, Dict, Tuple

import contextlib
from sqlalchemy import MetaData


@task
def create_database(db_conn_string: str) -> None:
    """Create the tables for the sqlalchemy model. This is idempotent.
    
    Arguments:
        db_conn_string {str} -- Connection string for the DB.
    """
    engine = create_engine(db_conn_string)
    Base.metadata.create_all(engine)


@task
def wipe_database(db_conn_string: str) -> None:
    """Wipe the records from the tables in the sqlalchemy model.
    
    Arguments:
        db_conn_string {str} -- Connection string for the DB.
    """
    engine = create_engine(db_conn_string)
    meta = Base.metadata

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()


@task
def load_data(input_tuple: Tuple) -> None:
    """Load data into a sqlalchemy table.
    
    Arguments:
        input_tuple {Tuple} -- A Tuple consisting of a connection string, a table class to load into, and records.
    """
    db_conn_string, table_class, records = input_tuple
    engine = create_engine(db_conn_string)
    Session = sessionmaker(bind=engine)
    sess = Session()

    sess.bulk_insert_mappings(table_class, records)
    count = sess.query(table_class).count()

    sess.commit()
    sess.close()
