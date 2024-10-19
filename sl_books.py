from fastapi import Body, APIRouter, Request, Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials

from constants import *
from data_validator import Book
from db_helper import insert_query, select_query, update_query, delete_query
from om_helper import *

router = APIRouter(tags=["books"], prefix="/books")


@router.post("/", response_model=dict)
@authorize_token
async def create_book(
    request: Request,
    book_details: dict = Body(...),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a new book.

    **Required Fields**:
    - **book_name**: Name of the book.
    - **book_price**: Price of the book.
    - **isbn**: ISBN of the book .
    - **library_id**: ID of the library where the book belongs.
    - **book_author**: Author of the book.

    **Optional Fields**:
    - **book_genre**: Genre of the book .
    - **publication**: Publication details.
    - **rentable**: Indicates if the book is rentable (default: True).
    - **status**: Current status of the book (default: 'available').
    """
    try:
        data = dict(book_details)
        response = insert_query(table_name=S_BOOK_TABLE, data=data)
        if response["status_bool"]:
            return success_json(records=response["records"], message="Added Successfully")
        return failure_json(status_code=S_BADREQUEST_CODE, message=response["message"])
    except ValueError as ve:
        return failure_json(message=f"{ve}", status_code=400)
    except Exception as e:
        return failure_json(message=f"{e}", status_code=500)

@router.get("/", response_model=dict)
@authorize_token
async def fetch_book(
    request: Request,
    library_id: int,
    record_id: int = None,
    book_name: str = None,
    status: str = None,
    isbn: str = None,
    num_records: int = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Fetch books based on specified criteria.

    - **library_id**: ID of the library to filter books.
    - **record_id**: Optional ID of a specific book.
    - **book_name**: Optional name of the book.
    - **status**: Optional status of the book.
    - **isbn**: Optional ISBN of the book.
    - **num_records**: Optional limit on the number of records returned.
    """
    conditions = {"library_id": library_id}
    if record_id is not None:
        conditions["id"] = record_id
    if book_name is not None:
        conditions["book_name"] = book_name
    if isbn is not None:
        conditions["isbn"] = isbn
    if status is not None:
        conditions["status"] = status

    select_response = select_query(table_name=S_BOOK_TABLE, conditions=conditions, num_records=num_records)
    if select_response:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)

@router.delete("/", response_model=dict)
@authorize_token
async def delete_book(
    request: Request,
    record_id: int,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a book by its ID.

    - **record_id**: ID of the book to be deleted.
    """
    delete_response = delete_query(table_name=S_BOOK_TABLE, record_id=record_id)[0]
    if delete_response["status_bool"]:
        return success_json(records=[], message="Record Deleted Successfully")
    return failure_json(message=f"Cannot Delete Record, {delete_response['message']}", status_code=S_BADREQUEST_CODE)

@router.patch("/", response_model=dict)
@authorize_token
async def update_book(
    request: Request,
    record_id: int,
    data: dict = Body(...),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update book details by its ID.

    - **record_id**: ID of the book to be updated.
    - **data**: Fields to be updated in the book record.
    """
    update_response = update_query(table_name=S_BOOK_TABLE, conditions={"id": record_id}, data=data)[0]
    if update_response["status_bool"]:
        return success_json(records=update_response["records"], message="Record Updated Successfully")
    return failure_json(message=f"Something Went Wrong, {update_response['message']}", status_code=S_BADREQUEST_CODE)
