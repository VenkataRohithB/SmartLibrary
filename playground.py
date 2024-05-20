import psycopg2

PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "library"
PG_USER = "rohith"
PG_PASSWORD = "Rohith@04"


class DB:

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.HOST = host
        self.PORT = port
        self.DATABASE = dbname
        self.USER = user
        self.PASSWORD = password
        try:
            self.conn = psycopg2.connect(
                user=self.USER, host=self.HOST, dbname=self.DATABASE, password=self.PASSWORD, port=self.PORT
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f"Connection failed: {e}")

    def __del__(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def create_table(self, table_name: str):
        try:
            self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY)""")
            self.conn.commit()
            print("Table Created")
        except Exception as e:
            print(f"Error in Creating table - [{e}]")

    def table_existence(self, table_name: str) -> bool:
        try:
            self.cur.execute(f"""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                )
            """)
            table_exists = self.cur.fetchone()[0]
            return table_exists
        except Exception as e:
            print(f"Error checking table existence - [{e}]")
            return False

    def add_field(self, table_name: str, field_name: str, field_type: str):
        try:
            if self.table_existence(table_name=table_name):
                self.cur.execute(query=f"""ALTER TABLE {table_name} ADD COLUMN {field_name} {field_type}""")
                self.conn.commit()
                print(f"{field_name} is added to {table_name}")

            else:
                print("Table does'nt exists")
        except Exception as e:
            print(f"Exception - add_field: [{e}]")

    def insert_record(self, table_name: str, record: dict):
        try:
            field_name = ",".join(record.keys())
            field_value = ",".join(["%s"] * len(record))
            insert_query = f"INSERT INTO {table_name} ({field_name}) VALUES ({field_value})"
            self.cur.execute(insert_query, list(record.values()))
            self.conn.commit()
        except Exception as e:
            print(f"Exception - insert_record: [{e}]")

    def update_record(self, id: int, table_name: str, record: dict):
        try:
            fields = ",".join(f"{field} = %s" for field in record)
            update_query = f"UPDATE {table_name} SET {fields} WHERE id = %s"
            self.cur.execute(update_query, list(record.values()) + [id])
            self.conn.commit()
            print(f"updated values {record}")
        except Exception as e:
            print(f"Exception - update_records: [{e}]")

    def delete_record(self, id: int, table_name: str):
        try:
            delete_query = f"DELETE FROM {table_name} where id = {id}"
            self.cur.execute(delete_query)
            self.conn.commit()
        except Exception as e:
            print(f"Exception - delete_record: [{e}]")


# Example usage:
obj = DB(host=PG_HOST, port=PG_PORT, dbname=PG_DATABASE, user=PG_USER, password=PG_PASSWORD)
# obj.create_table("testing101")
# if obj.table_existence("testing101"):
#     print("Table exists.")
# else:
#     print("Table does not exist.")
# obj.add_field(table_name="testing101", field_name="age", field_type="int")
# obj.insert_record(table_name="testing101", record={"name": "David", "age": 14})
# obj.update_record(id=2, table_name="testing101",record={"name":"Curran"})
obj.delete_record(id=2, table_name="testing101")
