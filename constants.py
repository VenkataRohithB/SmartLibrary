from enum import Enum
import os

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")
SENDGRID_API = os.getenv("SENDGRID_API")


TOKEN_ALGORITHM = "HS256"

# STATUS CODES
S_BADREQUEST_CODE = 400
S_NOTFOUND_CODE = 404
S_SUCCESS_CODE = 200
S_UNAUTHORIZED_CODE = 401
S_FORBIDDEN_CODE = 403
S_INTERNALERROR_CODE = 500

# TABLE NAMES
S_USER_TABLE = "USERS"
S_OTP_TABLE = "OTP"
S_LIBRARY_TABLE = "LIBRARY"
S_LIBRARY_USER_TABLE = "LIBRARY_USER"
S_BOOK_TABLE = "BOOK"
S_RENTAL_TABLE = "RENTAL"
S_PENALTY_PAYMENT_TABLE = "PENALTY_PAYMENT"

# ViEW NAMES
S_LIBRARY_USER_VIEW = "LIBRARY_USER_DETAILS"
S_RENTAL_PENALTY_VIEW = "PENALTY"
S_RENTAL_VIEW = "RENTAL_DETAILS"

# CONSTRAINTS
S_NOT_NULL = "NOT NULL"
S_UNIQUE = "NOT NULL UNIQUE"

# EXPIRY TIME
OTP_VALID_TIME = 5
MEMBERSHIP_EXPIRY_DAYS = 365

S_BOOK_RENTAL_EXPIRY = 0.001
S_USER_BOOK_LIMIT = 5

# BOOK_STATUS
S_BOOK_AVAILABLE = "available"
S_BOOK_RESERVED = "reserved"
S_BOOK_RENTED = "rented"

SECRET_KEY = "11923"


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Book_Status(Enum):
    RESERVED = "rented"
    RETURNED = "available"
