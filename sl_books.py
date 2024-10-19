from fastapi import Body, APIRouter, Request, Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials

from constants import *
from data_validator import Book
from db_helper import insert_query, select_query, update_query, delete_query
from om_helper import *

router = APIRouter(tags=["books"], prefix="/books")


@router.post("/")
@authorize_token
async def create_book(request: Request, book_details: Book = Body(...),
                      token: HTTPAuthorizationCredentials = Depends(security)):
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


@router.get("/")
@authorize_token
async def fetch_book(request: Request, library_id: int, record_id: int = None, book_name: str = None,
                     status: Book_Status = None, isbn: str = None,
                     num_records: int = None,
                     token: HTTPAuthorizationCredentials = Depends(security)):
    conditions = {"library_id": library_id}
    if record_id is not None:
        conditions["id"] = record_id
    if book_name is not None:
        conditions["book_name"] = book_name
    if isbn is not None:
        conditions["isbn"] = isbn
    if status is not None:
        conditions["status"] = status.value

    select_response = select_query(table_name=S_BOOK_TABLE, conditions=conditions, num_records=num_records)
    if select_response:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)


@router.delete("/")
@authorize_token
async def delete_book(request: Request, record_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    delete_response = delete_query(table_name=S_BOOK_TABLE, record_id=record_id)[0]
    if delete_response["status_bool"]:
        return success_json(records=[], message="Record Deleted Successfully")
    return failure_json(message=f"Cannot Delete Record, {delete_response["message"]}", status_code=S_BADREQUEST_CODE)


@router.patch("/")
@authorize_token
async def update_book(request: Request, record_id: int, data: dict = Body(...),
                      token: HTTPAuthorizationCredentials = Depends(security)):
    update_response = update_query(table_name=S_BOOK_TABLE, conditions={"id": record_id}, data=data)[0]
    if update_response["status_bool"]:
        return success_json(records=update_response["records"], message="Record Updated Successfully")
    return failure_json(message=f"Something Went Wrong, {update_response["message"]}", status_code=S_BADREQUEST_CODE)
