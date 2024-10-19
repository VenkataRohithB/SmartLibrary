from pydantic import BaseModel, Field
from typing import Optional


class Users(BaseModel):
    user_name: str
    user_phone: str
    user_email: str
    user_password: str
    user_address: Optional[str] = None
    status: str = Field(default='active')
    user_type: str = Field(default='member')
    user_otp: Optional[str] = None
    membership_expiry: Optional[str] = None
    user_checkin: bool = Field(default=False)
    otp_expiry: Optional[str] = None


class Book(BaseModel):
    book_name: str
    book_price: int
    isbn: str
    library_id: int
    book_author: str
    book_genre: Optional[str] = None
    publication: Optional[str] = None
    rentable: bool = Field(default=True)
    status: str = Field(default='available')
