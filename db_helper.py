from db_funcs import *
from constants import *

db_conn = DB_Manager()


def select_query(table_name: str, columns: dict = None, conditions: dict = None, num_records: int = None):
    response = db_conn.select_query(table_name=table_name, get_items=columns, condition_dict=conditions,
                                    num_records=num_records)
    return response


def insert_query(table_name: str, data: dict):
    response = db_conn.insert_data(table_name=table_name, data=data)
    return response


def update_query(table_name: str, conditions: dict, data: dict):
    response = db_conn.update_data(table_name=table_name, conditions=conditions, data=data)
    return response


def delete_query(table_name: str, record_id: int):
    response = db_conn.delete_data(table_name=table_name, record_id=record_id)
    return response
