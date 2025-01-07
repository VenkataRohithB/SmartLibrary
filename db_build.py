from db_funcs import *
from constants import *


db_conn = DB_Manager()

# db_conn.drop_table(table_name=S_USER_TABLE)
# db_conn.drop_table(table_name=S_LIBRARY_TABLE)
# db_conn.drop_table(table_name=S_LIBRARY_USER_TABLE)
# db_conn.drop_view(view_name=S_LIBRARY_USER_VIEW)
# db_conn.drop_table(table_name=S_BOOK_TABLE)
# db_conn.drop_table(table_name=S_RENTAL_TABLE)
# db_conn.drop_view(view_name=S_RENTAL_VIEW)
db_conn.drop_view(view_name=S_RENTAL_PENALTY_VIEW)
# db_conn.drop_table(table_name=S_PENALTY_PAYMENT_TABLE)



# print(f"\n==================== Creating Table :[{S_USER_TABLE}] =====================")
# db_conn.create_table(table_name=S_USER_TABLE)
# db_conn.add_field(table_name=S_USER_TABLE, field_name="status", field_type="varchar(8)", constraints="DEFAULT 'active'")
# db_conn.add_field(table_name=S_USER_TABLE, field_name="user_name", field_type="varchar(100)", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_USER_TABLE, field_name="user_phone", field_type="varchar(10)", constraints=S_UNIQUE)
# db_conn.add_field(table_name=S_USER_TABLE, field_name="user_type", field_type="varchar(10)", constraints="DEFAULT 'member'")
# db_conn.add_field(table_name=S_USER_TABLE,field_name="user_email", field_type="varchar(100)", constraints=S_UNIQUE)
# db_conn.add_field(table_name=S_USER_TABLE, field_name="user_password", field_type="varchar(30)",constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_USER_TABLE, field_name="user_address", field_type="varchar(150)")
# db_conn.add_field(table_name=S_USER_TABLE,field_name="user_otp", field_type="varchar(6)")
# db_conn.add_field(table_name=S_USER_TABLE,field_name="user_active_books", field_type="integer",constraints="DEFAULT '0'")
# db_conn.add_field(table_name=S_USER_TABLE, field_name="membership_expiry", field_type="timestamp", constraints=f"DEFAULT (CURRENT_TIMESTAMP + INTERVAL '{MEMBERSHIP_EXPIRY_DAYS} days')")
# db_conn.add_field(table_name=S_USER_TABLE, field_name="user_checkin", field_type="bool",constraints="DEFAULT false")
# db_conn.add_field(table_name=S_USER_TABLE,field_name="otp_expiry", field_type="TIMESTAMP")
#
#
# print(f"\n==================== Creating Table :[{S_LIBRARY_TABLE}] =====================")
# db_conn.create_table(table_name=S_LIBRARY_TABLE)
# db_conn.add_field(table_name=S_LIBRARY_TABLE, field_name="status", field_type="varchar(8)", constraints="DEFAULT 'active'")
# db_conn.add_field(table_name=S_LIBRARY_TABLE,field_name="library_name", field_type="varchar(50)", constraints=S_UNIQUE)
# db_conn.add_field(table_name=S_LIBRARY_TABLE,field_name="library_address", field_type="varchar(150)", constraints=S_NOT_NULL)
#
# print(f"\n==================== Creating Table :[{S_LIBRARY_USER_TABLE}] =====================")
# db_conn.create_table(table_name=S_LIBRARY_USER_TABLE)
# db_conn.add_field(table_name=S_LIBRARY_USER_TABLE, field_name="user_id", field_type="integer", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_LIBRARY_USER_TABLE, field_name="library_id", field_type="integer", constraints=S_NOT_NULL)
#
# print(f"\n==================== Creating View :[{S_LIBRARY_USER_VIEW}] =====================")
# query = sql.SQL("""
#     CREATE VIEW {view_name} AS
#     SELECT
#         r.id AS id,
#         l.id AS library_id,
#         u.id AS user_id,
#         l.library_name,
#         l.status as library_status,
#         u.status as user_status,
#         u.user_name as user_name,
#         u.user_phone as user_phone,
#         u.user_email as user_email,
#         u.user_type,
#         l.library_address,
#         u.user_address
#     FROM
#         {relation_table} r
#     JOIN
#         {user_table} u ON r.user_id = u.id
#     JOIN
#         {library_table} l ON r.library_id = l.id;
# """).format(view_name=sql.Identifier(S_LIBRARY_USER_VIEW), relation_table=sql.Identifier(S_LIBRARY_USER_TABLE),
#             user_table=sql.Identifier(S_USER_TABLE), library_table=sql.Identifier(S_LIBRARY_TABLE))
#
# print(db_conn.execute_query(query=query, insert=False))
#
#
# print(f"\n==================== Creating Table :[{S_BOOK_TABLE}] =====================")
# db_conn.create_table(table_name=S_BOOK_TABLE)
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="status", field_type="varchar(20)", constraints="DEFAULT 'available'")
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="book_name", field_type="varchar(50)", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="book_price", field_type="integer", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="isbn", field_type="varchar(30)", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="library_id", field_type="integer", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="book_author", field_type="varchar(30)", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="book_genre", field_type="varchar(20)")
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="publication", field_type="varchar(100)")
# db_conn.add_field(table_name=S_BOOK_TABLE, field_name="rentable", field_type="boolean", constraints="DEFAULT true")
# db_conn.add_foreign_key(table_name=S_BOOK_TABLE, field_name="library_id", ref_table=S_LIBRARY_TABLE, ref_field="id")
#
# print(f"\n==================== Creating Table :[{S_RENTAL_TABLE}] =====================")
# db_conn.create_table(table_name=S_RENTAL_TABLE)
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="status", field_type="varchar(10)", constraints="DEFAULT 'active'")
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="user_id", field_type="integer", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="book_id", field_type="integer", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="rented_on", field_type="timestamp", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="valid_till", field_type="timestamp", constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="returned_on", field_type="timestamp")
# db_conn.add_field(table_name=S_RENTAL_TABLE, field_name="penalty_paid", field_type="boolean", constraints="DEFAULT true")
# db_conn.add_foreign_key(table_name=S_RENTAL_TABLE, field_name="user_id", ref_table=S_USER_TABLE, ref_field="id")
# db_conn.add_foreign_key(table_name=S_RENTAL_TABLE, field_name="book_id", ref_table=S_BOOK_TABLE, ref_field="id")
#
# print(f"\n==================== Creating Table :[{S_RENTAL_VIEW}] =====================")
# view_query = sql.SQL("""CREATE VIEW {view_name} AS SELECT
#     r.id as id,
#     u.id as user_id,
#     u.user_name,
#     u.user_phone,
#     u.user_email,
#     u.user_type,
#     b.id as book_id,
#     b.book_name,
#     b.book_price,
#     b.isbn,
#     b.library_id,
#     r.status,
#     r.rented_on,
#     r.valid_till,
#     r.returned_on,
#     r.penalty_paid
# FROM
#     {rented_table} r
# JOIN
#     {user_table} u ON r.user_id = u.id
# JOIN
#     {book_table} b ON r.book_id = b.id;
# """).format(view_name=sql.Identifier(S_RENTAL_VIEW),
#             rented_table=sql.Identifier(S_RENTAL_TABLE),
#             user_table=sql.Identifier(S_USER_TABLE),
#             book_table=sql.Identifier(S_BOOK_TABLE))
# print(db_conn.execute_query(query=view_query, insert=False))
#
# print(f"\n==================== Creating Table :[{S_PENALTY_PAYMENT_TABLE}] =====================")
# db_conn.create_table(table_name=S_PENALTY_PAYMENT_TABLE)
# db_conn.add_field(table_name=S_PENALTY_PAYMENT_TABLE, field_name="rental_id", field_type="integer",
#                   constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_PENALTY_PAYMENT_TABLE, field_name="amount_paid", field_type="integer",
#                   constraints=S_NOT_NULL)
# db_conn.add_field(table_name=S_PENALTY_PAYMENT_TABLE, field_name="paid_on", field_type="timestamp",
#                   constraints="DEFAULT CURRENT_TIMESTAMP")
# db_conn.add_field(table_name=S_PENALTY_PAYMENT_TABLE, field_name="payment_method", field_type="varchar(30)")
# db_conn.add_foreign_key(table_name=S_PENALTY_PAYMENT_TABLE, field_name="rental_id", ref_table=S_RENTAL_TABLE,
#                         ref_field="id")

print(f"\n==================== Creating View :[{S_RENTAL_PENALTY_VIEW}] =====================")
view_query = sql.SQL("""
CREATE VIEW {view_name} AS
SELECT
    r.id AS rental_id,
    b.id AS book_id,
    b.book_name AS book_name,
    b.book_price AS book_price,
    b.library_id as library_id,
    u.id AS user_id,
    u.user_phone AS user_phone,
    u.user_email AS user_email,
    r.rented_on AS rented_on,
    r.valid_till AS valid_till,
    r.returned_on AS returned_on,
    r.penalty_paid AS penalty_paid,
    CASE
    WHEN r.returned_on > r.valid_till
    THEN ROUND(b.book_price * 0.01 * EXTRACT(DAY FROM r.returned_on - r.valid_till))::INTEGER
    ELSE 0
END AS calculated_penalty

FROM
    {rented_table} r
JOIN
    {user_table} u ON r.user_id = u.id
JOIN
    {book_table} b ON r.book_id = b.id
WHERE
    r.penalty_paid = false;
""").format(
    view_name=sql.Identifier(S_RENTAL_PENALTY_VIEW),
    rented_table=sql.Identifier(S_RENTAL_TABLE),
    user_table=sql.Identifier(S_USER_TABLE),
    book_table=sql.Identifier(S_BOOK_TABLE)
)

print(db_conn.execute_query(query=view_query, insert=False))
