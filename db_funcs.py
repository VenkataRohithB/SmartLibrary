import re

import psycopg2
from psycopg2 import sql, extras, IntegrityError, DataError, DatabaseError, OperationalError, ProgrammingError
from constants import *
from datetime import datetime


def parse_pgresponse(data):
    if not data:
        return data

    def format_row(row):
        return {
            key: (value.strftime('%Y-%m-%d %H:%M:%S.%f') if isinstance(value, datetime) else value)
            for key, value in row.items()
        }

    if isinstance(data, list):
        return [format_row(row) for row in data]
    return [format_row(data)]


class DB_Manager:
    def __init__(self):
        self.connection = None
        self.connect_to_db()

    def connect_to_db(self):
        db_config = {"host": PG_HOST, "dbname": PG_DATABASE, "user": PG_USER, "password": PG_PASSWORD, "port": PG_PORT}
        try:
            self.connection = psycopg2.connect(**db_config)
            print("Connection with DB established successfully")
        except Exception as e:
            print(f"Cannot establish connection with DB: [{e}]")

    def create_table(self, table_name: str) -> bool:
        query = sql.SQL("""CREATE TABLE IF NOT EXISTS {table}
         (
         id SERIAL PRIMARY KEY,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
         )
         """).format(table=sql.Identifier(table_name))
        if self.execute_query(query=query, insert=False):
            print(f"Table: [{table_name}] Created Successfully")
            return True
        print(f"create_table: [{table_name}] Something Went Wrong")
        return False

    def add_field(self, table_name: str, field_name: str, field_type: str, constraints: str = None) -> bool:
        field_definition = sql.SQL("{type}").format(type=sql.SQL(field_type))

        if constraints:
            field_definition += sql.SQL(" ") + sql.SQL(constraints)

        query = sql.SQL("ALTER TABLE {table} ADD COLUMN {field} {definition}").format(
            table=sql.Identifier(table_name),
            field=sql.Identifier(field_name),
            definition=field_definition)
        response = self.execute_query(query=query, insert=False)
        if response["status_bool"]:
            print(f"Field: [{field_name}] added to Table: [{table_name}]")
            return True
        print(f"Error in Adding Field: [{response}]")
        return False

    def add_foreign_key(self, table_name: str, field_name: str, ref_table: str, ref_field: str) -> bool:
        query = sql.SQL(
            "ALTER TABLE {table} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({field}) REFERENCES {ref_table}({ref_field})")
        query = query.format(table=sql.Identifier(table_name),
                             constraint_name=sql.Identifier(f"{table_name}_{field_name}_fk"),
                             field=sql.Identifier(field_name),
                             ref_table=sql.Identifier(ref_table),
                             ref_field=sql.Identifier(ref_field))

        response = self.execute_query(query=query, insert=False)
        if response["status_bool"]:
            print(f"Foreign key constraint added to {field_name} in {table_name}, referencing {ref_table}({ref_field})")
            return True
        print(f"Error in Adding Foreign key: [{response}]")
        return False

    def drop_table(self, table_name: str) -> bool:
        query = sql.SQL("DROP TABLE IF EXISTS {table} CASCADE").format(table=sql.Identifier(table_name))
        response = self.execute_query(query=query, insert=False)
        if response["status_bool"]:
            print(f"Table: [{table_name}] is Deleted")
            return True
        print(f"Error in Deleting Table: [{response}]")
        return False

    def drop_view(self, view_name: str) -> bool:
        query = sql.SQL("DROP VIEW IF EXISTS {view} CASCADE").format(view=sql.Identifier(view_name))
        response = self.execute_query(query=query, insert=False)
        if response["status_bool"]:
            print(f"View: [{view_name}] is Deleted")
            return True
        print(f"Error in Deleting view: [{response}]")
        return False

    def select_query(self, table_name: str, get_items: list = None, condition_dict: dict = None,
                     num_records: int = None):
        # Base Query Build
        if get_items:
            columns = sql.SQL(", ").join(sql.Identifier(col) for col in get_items)
        else:
            columns = sql.SQL("*")
        query = sql.SQL("SELECT {columns} from {table}").format(columns=columns, table=sql.Identifier(table_name))

        # Adding condition (All AND)
        if condition_dict:
            conditions = sql.SQL(" WHERE ")
            conditions += sql.SQL(" AND ").join(
                sql.Composed([sql.Identifier(key), sql.SQL(" = "), sql.Placeholder(key)]) for key in condition_dict)
            query = query + conditions

        # Adding num_records
        if num_records:
            query += sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(num_records))

        records = self.fetch_all(query=query, params=condition_dict)
        return parse_pgresponse(records)

    def insert_data(self, table_name: str, data: dict):
        fields = sql.SQL(", ").join(sql.Identifier(field) for field in data)
        values = sql.SQL(", ").join(sql.Placeholder(field) for field in data)
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING *").format(
            table=sql.Identifier(table_name),
            fields=fields, values=values)
        records = self.execute_query(query=query, params=data)
        return records

    def update_data(self, table_name: str, conditions: dict, data: dict):
        data["updated_at"] = datetime.now()

        update_query = sql.SQL(", ").join(
            sql.Composed([sql.Identifier(key), sql.SQL(" = "), sql.Placeholder(key)]) for key in data
        )

        condition_query = sql.SQL(" AND ").join(
            sql.Composed([sql.Identifier(key), sql.SQL(" = "), sql.Placeholder(f"cond_{key}")]) for key in conditions
        )

        params = {**data, **{f"cond_{key}": value for key, value in conditions.items()}}

        query = sql.SQL("UPDATE {table} SET {update_query} WHERE {condition_query} RETURNING *").format(
            table=sql.Identifier(table_name),
            update_query=update_query,
            condition_query=condition_query
        )

        records = self.execute_query(query=query, params=params)
        return parse_pgresponse(records)

    def delete_data(self, table_name: str, record_id: int):
        query = sql.SQL("DELETE FROM {table} WHERE id = {id} RETURNING *").format(table=sql.Identifier(table_name),
                                                                                  id=sql.Placeholder("id"))
        params = {"id": record_id}
        records = self.execute_query(query=query, params=params)
        return parse_pgresponse(data=records)

    def execute_query(self, query, params=None, insert=True):
        try:
            with self.connection.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                self.connection.commit()

                if insert:
                    inserted_record = cursor.fetchone()
                    return {
                        "status_bool": True,
                        "records": parse_pgresponse(inserted_record),
                        "message": "Query executed successfully"
                    }

                return {
                    "status_bool": True,
                    "records": None,
                    "message": "Query executed successfully"
                }

        except IntegrityError as e:
            error_message = str(e)
            self.connection.rollback()
            not_null_match = re.search(r'null value in column "(.*?)" violates not-null constraint', error_message)
            if not_null_match:
                column_name = not_null_match.group(1)
                return {
                    "status_bool": False,
                    "message": f"Mandatory Field: {column_name} is Missing"
                }

            unique_violation_match = re.search(r'duplicate key value violates unique constraint "(.*?)"', error_message)
            if unique_violation_match:
                field_match = re.search(r'Key \((.*?)\)=\(', error_message)
                if field_match:
                    column_name = field_match.group(1)
                    return {
                        "status_bool": False,
                        "message": f"{column_name} Already Exists"
                    }

            foreign_key_violation_match = re.search(
                r'insert or update on table "(.*?)" violates foreign key constraint', error_message)
            if foreign_key_violation_match:
                return {
                    "status_bool": False,
                    "message": "Foreign key constraint violation."
                }

            return {
                "status_bool": False,
                "message": f"Integrity error: {error_message}"
            }

        except DataError as e:
            self.connection.rollback()
            return {
                "status_bool": False,
                "message": f"Invalid data error: {str(e)}."
            }

        except OperationalError as e:
            self.connection.rollback()
            return {
                "status_bool": False,
                "message": f"Operational error: {str(e)}."
            }

        except ProgrammingError as e:
            self.connection.rollback()
            return {
                "status_bool": False,
                "message": f"Programming error: {str(e)}."
            }

        except DatabaseError as e:
            self.connection.rollback()
            return {
                "status_bool": False,
                "message": f"Database error: {str(e)}."
            }

        except Exception as e:
            self.connection.rollback()
            return {
                "status_bool": False,
                "message": f"An unexpected error occurred: {str(e)}."
            }

    def fetch_all(self, query, params=None, error_msg=None):
        try:
            with self.connection.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            print(f"{error_msg} - [{e}]")
            return None
