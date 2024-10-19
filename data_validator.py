from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, List
import re


class Users(BaseModel):
    user_name: str
    user_phone: str
    user_email: str
    user_password: str
    user_address: str = None


class Library(BaseModel):
    library_name: str
    library_address: str


class Book(BaseModel):
    book_name: str
    book_price: int
    isbn: str
    library_id: int
    book_author: str
