from fastapi import Body, APIRouter, Request, Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials

from constants import *
from data_validator import Users
from db_helper import insert_query, select_query, update_query, delete_query
from om_helper import *
import json

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=dict)
@authorize_token
async def create_user(
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(security),
        user_info: dict = Body(...)
):
    """
    Create a new user.

    **Required Fields**:
    - **user_name**: The name of the user.
    - **user_phone**: The phone number of the user (must be unique).
    - **user_email**: The email address of the user (must be unique).
    - **user_password**: The password for the user account.

    **Optional Fields**:
    - **user_address**: The address of the user (default: None).
    - **status**: The current status of the user (default: 'active').
    - **user_type**: Type of user, such as 'member' (default: 'member').
    """
    try:
        user_details = dict(user_info)
        validate_response = validate_user_fields(user_details=user_details)
        if validate_response is not None:
            return failure_json(message=validate_response, status_code=S_BADREQUEST_CODE)
        insert_response = insert_query(table_name=S_USER_TABLE, data=user_details)
        if not insert_response["status_bool"]:
            return failure_json(message=insert_response["message"], status_code=400)
        return success_json(records=insert_response["records"])
    except ValueError as ve:
        return failure_json(message=f"{ve}", status_code=400)
    except Exception as e:
        return failure_json(message=f"{e}", status_code=500)


@router.get("/", response_model=dict)
@authorize_token
async def fetch_user(
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(security),
        record_id: int = None,
        user_phone: str = None,
        num_records: int = None
):
    """
    Fetch users based on specified criteria.

    - **record_id**: Optional ID of a specific user.
    - **user_phone**: Optional phone number of the user.
    - **num_records**: Optional limit on the number of records returned.
    """
    conditions = {}
    if record_id is not None:
        conditions["id"] = record_id
    if user_phone is not None:
        conditions["user_phone"] = user_phone
    select_response = select_query(table_name=S_USER_TABLE, conditions=conditions, num_records=num_records)
    if select_response != []:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)


@router.patch("/", response_model=dict)
@authorize_token
async def update_user(
        request: Request,
        record_id: int,
        data: dict = Body(...),
        token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update user details by their ID.

    - **record_id**: ID of the user to be updated.
    - **data**: Fields to be updated in the user record.
    """
    select_response = select_query(table_name=S_USER_TABLE, conditions={"id": record_id})
    if select_response:
        if data.get("id"):
            return failure_json(message="Cannot update any of these: ['id', 'user_phone', 'user_email']",
                                status_code=S_BADREQUEST_CODE)
        validation_response = validate_user_fields(user_details=data)
        if validation_response is not None:
            return failure_json(message=validation_response, status_code=S_BADREQUEST_CODE)
        update_response = update_query(table_name=S_USER_TABLE, conditions={"id": record_id}, data=data)[0]
        if update_response["status_bool"]:
            return success_json(records=update_response["records"], message="User Updated Successfully")
        return failure_json(message=update_response["message"], status_code=S_BADREQUEST_CODE)
    return failure_json(message="User Not Found", status_code=S_NOTFOUND_CODE)


@router.delete("/", response_model=dict)
@authorize_token
async def delete_user(
        request: Request,
        record_id: int,
        token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a user by their ID.

    - **record_id**: ID of the user to be deleted.
    """
    delete_response = delete_query(table_name=S_USER_TABLE, record_id=record_id)[0]
    if delete_response["status_bool"]:
        return success_json(records=delete_response["records"], message="User Deleted Successfully")
    return failure_json(message="Record Cannot be Deleted", status_code=S_BADREQUEST_CODE)
