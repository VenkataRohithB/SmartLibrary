from fastapi import Body, APIRouter, Request, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta

from constants import *
from db_helper import insert_query, select_query, update_query
from om_helper import *

router = APIRouter(tags=["transactions"], prefix="/transactions")


@router.post("/rent_book",
             summary="Rent a book",
             description="Allows a user to rent a book from the library. "
                         "Validates user check-in and book availability.")
async def rent(
    request: Request,
    user_id: int,
    book_id: int,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    user = select_query(table_name=S_USER_TABLE, conditions={"id": user_id})[0]
    book = select_query(table_name=S_BOOK_TABLE, conditions={"id": book_id})[0]

    if user and book:
        if not user["user_checkin"]:
            return failure_json(message="User is Not in Library, Please Check In With Pass.", status_code=S_FORBIDDEN_CODE)

        user_library_check = select_query(table_name=S_LIBRARY_USER_TABLE,
                                          conditions={"user_id": user_id, "library_id": book["library_id"]})

        if not user_library_check:
            return failure_json(message="User is not registered in the library where the book is located.", status_code=S_FORBIDDEN_CODE)

        exists_check = select_query(table_name=S_RENTAL_TABLE,
                                    conditions={"user_id": user_id, "book_id": book_id, "status": "active"})
        if exists_check:
            return failure_json(message="Book Already Exists with the user", status_code=S_BADREQUEST_CODE)

        penalty_check = select_query(table_name=S_RENTAL_PENALTY_VIEW,
                                     conditions={"user_id": user_id, "penalty_paid": False})
        if penalty_check:
            return failure_json(message="Penalty Pending, User cannot rent a book", status_code=S_BADREQUEST_CODE)

        if user["status"] != "active":
            return failure_json(message="User Not Active", status_code=S_BADREQUEST_CODE)

        if book["status"] != "available":
            return failure_json(message=f"Book is not available - [{book['status']}]", status_code=S_BADREQUEST_CODE)

        valid_till = parse_timestamp(str_timestamp=current_time()) + timedelta(days=S_BOOK_RENTAL_EXPIRY)
        rental_data = {"rented_on": current_time(), "book_id": book_id, "user_id": user_id, "valid_till": valid_till}
        create_response = insert_query(table_name=S_RENTAL_TABLE, data=rental_data)

        if create_response["status_bool"]:
            update_query(table_name=S_BOOK_TABLE, conditions={"id": book_id}, data={"status": "rented"})
            final_response = select_query(table_name=S_RENTAL_VIEW,
                                          conditions={"id": create_response["records"][0]["id"]})
            return success_json(records=final_response, message="Transaction Completed.")

        return failure_json(message=create_response["message"], status_code=S_BADREQUEST_CODE)

    return failure_json(message="Invalid user or book details", status_code=S_BADREQUEST_CODE)


@router.patch("/return_book",
               summary="Return a rented book",
               description="Allows a user to return a rented book. "
                           "Checks if the user is checked in and updates the rental status.")
async def return_book(
    request: Request,
    user_id: int,
    book_id: int,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    rent_history = select_query(table_name=S_RENTAL_TABLE,
                                conditions={"user_id": user_id, "book_id": book_id, "status": "active"})
    if not rent_history:
        return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)

    user = select_query(table_name=S_USER_TABLE, conditions={"id": user_id})[0]
    if not user["user_checkin"]:
        return failure_json(message="User Not in Library, Please Check In with Pass", status_code=S_BADREQUEST_CODE)

    data = {"status": "inactive", "returned_on": current_time()}
    if parse_timestamp(str_timestamp=current_time()) > parse_timestamp(str_timestamp=rent_history[0]["valid_till"]):
        data["penalty_paid"] = False

    update_response = update_query(table_name=S_RENTAL_TABLE, conditions={"id": rent_history[0]["id"]}, data=data)[0]
    if update_response["status_bool"]:
        update_query(table_name=S_BOOK_TABLE, conditions={"id": book_id}, data={"status": "available"})
        final_response = select_query(table_name=S_RENTAL_VIEW, conditions={"id": update_response["records"][0]["id"]})
        return success_json(records=final_response, message="Transaction Successful.")

    return failure_json(message=f"Something went wrong - {update_response['message']}", status_code=S_BADREQUEST_CODE)


@router.get("/rented_books",
            summary="Get rented books",
            description="Retrieves a list of rented books based on specified filters. "
                        "At least one parameter must be provided.")
async def rented_books(
    request: Request,
    library_id: int = Query(None, description="The ID of the library to filter rented books"),
    status: str = Query(None, description="Status of the rented books (e.g., active, inactive)"),
    book_id: int = Query(None, description="The ID of the book to filter results"),
    user_id: int = Query(None, description="The ID of the user to filter results"),
    num_records: int = Query(None, description="Number of records to retrieve"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    conditions = {}

    if library_id:
        conditions["library_id"] = library_id
    if status:
        conditions["status"] = status
    if book_id:
        conditions["book_id"] = book_id
    if user_id:
        conditions["user_id"] = user_id

    if not conditions:
        return failure_json(message="Please Enter At least 1 Parameter", status_code=S_BADREQUEST_CODE)

    select_response = select_query(table_name=S_RENTAL_VIEW, conditions=conditions, num_records=num_records)
    if select_response:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)


@router.get("/penalties",
            summary="Get penalties",
            description="Retrieves penalty records for users based on specified filters. "
                        "At least one parameter must be provided.")
async def penalties(
    request: Request,
    library_id: int = Query(None, description="The ID of the library to filter penalties"),
    user_id: int = Query(None, description="The ID of the user to filter penalties"),
    rental_id: int = Query(None, description="The rental ID to filter penalties"),
    num_records: int = Query(None, description="Number of records to retrieve"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    conditions = {}

    if library_id:
        conditions["library_id"] = library_id
    if user_id:
        conditions["user_id"] = user_id
    if rental_id:
        conditions["rental_id"] = rental_id
    if not conditions:
        return failure_json(message="Please Enter At least 1 Parameter", status_code=S_BADREQUEST_CODE)

    select_response = select_query(table_name=S_RENTAL_PENALTY_VIEW, conditions=conditions, num_records=num_records)
    if select_response:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)


@router.post("/paid_penalty",
              summary="Pay a penalty",
              description="Allows users to pay their penalties. "
                          "Updates the penalty status after payment.")
async def pay_penalty(
    request: Request,
    rental_id: int,
    amount_paid: int,
    payment_method: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    select_response = select_query(table_name=S_RENTAL_TABLE, conditions={"id": rental_id, "penalty_paid": False})
    if not select_response:
        return failure_json(message="No Penalties Found.", status_code=S_NOTFOUND_CODE)

    insert_response = insert_query(table_name=S_PENALTY_PAYMENT_TABLE, data={"rental_id": rental_id, "amount_paid": amount_paid, "payment_method": payment_method})
    update_response = update_query(table_name=S_RENTAL_TABLE, conditions={"id": rental_id}, data={"penalty_paid": True})

    if update_response[0]["status_bool"]:
        select_response = select_query(table_name=S_RENTAL_VIEW, conditions={"id": rental_id})
        return success_json(records=select_response)

    return failure_json(message="Something went wrong", status_code=S_BADREQUEST_CODE)
