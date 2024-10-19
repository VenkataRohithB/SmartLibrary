from fastapi import Body, APIRouter, Request, Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials

from constants import *
from data_validator import Library
from db_helper import insert_query, select_query, update_query, delete_query
from om_helper import *

router = APIRouter(tags=["library"], prefix="/library")


@router.post("/")
@authorize_token
async def add_library(request: Request, library_name: str, library_address: str,
                      token: HTTPAuthorizationCredentials = Depends(security)):
    data = {"library_name": library_name, "library_address": library_address}
    response = insert_query(table_name=S_LIBRARY_TABLE, data=data)
    if response["status_bool"]:
        return success_json(records=response["records"], message="Added Successfully")
    return failure_json(status_code=S_BADREQUEST_CODE, message=response["message"])


@router.get("/")
@authorize_token
async def fetch_library(request: Request, record_id: int = None, library_name: str = None, num_records: int = None,
                        token: HTTPAuthorizationCredentials = Depends(security)):
    conditions = {}
    if record_id is not None:
        conditions["id"] = record_id
    if library_name is not None:
        conditions["library_name"] = library_name
    select_response = select_query(table_name=S_LIBRARY_TABLE, conditions=conditions, num_records=num_records)
    if select_response:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)


@router.delete("/")
@authorize_token
async def delete_library(request: Request, record_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    delete_response = delete_query(table_name=S_LIBRARY_TABLE, record_id=record_id)[0]
    if delete_response["status_bool"]:
        return success_json(records=[], message="Record Deleted Successfully")
    return failure_json(message=f"Cannot Delete Record, {delete_response["message"]}", status_code=S_BADREQUEST_CODE)


@router.patch("/")
@authorize_token
async def update_library(request: Request, record_id: int, data: dict = Body(...),
                         token: HTTPAuthorizationCredentials = Depends(security)):
    update_response = update_query(table_name=S_LIBRARY_TABLE, conditions={"id": record_id}, data=data)[0]
    if update_response["status_bool"]:
        return success_json(records=update_response["records"], message="Record Updated Successfully")
    return failure_json(message=f"Something Went Wrong, {update_response["message"]}", status_code=S_BADREQUEST_CODE)


@router.post("/users")
@authorize_token
async def user_library(request: Request, library_id: int, user_id: int,
                       token: HTTPAuthorizationCredentials = Depends(security)):
    user = select_query(table_name=S_USER_TABLE, conditions={"id": user_id})
    library = select_query(table_name=S_LIBRARY_TABLE, conditions={"id": library_id})
    if not user:
        return failure_json(message="User Not Found.", status_code=S_NOTFOUND_CODE)
    elif not library:
        return failure_json(message="Library Not Found.", status_code=S_NOTFOUND_CODE)
    library_user = select_query(table_name=S_LIBRARY_USER_TABLE,
                                conditions={"user_id": user_id, "library_id": library_id})
    if library_user:
        return failure_json(message=f"User Already Exists in Library - [{library_id}].", status_code=S_BADREQUEST_CODE)
    result = insert_query(table_name=S_LIBRARY_USER_TABLE, data={"library_id": library_id, "user_id": user_id})
    if result["status_bool"]:
        relation_id = result["records"][0]['id']
        select_response = select_query(table_name=S_LIBRARY_USER_VIEW, conditions={"id": relation_id})
        return success_json(records=select_response, message=f"User Added to Library - [{library_id}]")
    return failure_json(message="Something Went Wrong", status_code=S_BADREQUEST_CODE)


@router.get("/users")
@authorize_token
async def fetch_library_user(request: Request, library_id: int = None, user_id: int = None, user_status: Status = None,
                             num_records: int = None,
                             token: HTTPAuthorizationCredentials = Depends(security)):
    conditions = {}
    if library_id is not None:
        conditions["library_id"] = library_id
    if user_id is not None:
        conditions["user_id"] = user_id
    if user_status is not None:
        conditions["status"] = user_status.value
    select_response = select_query(table_name=S_LIBRARY_USER_VIEW, conditions=conditions, num_records=num_records)
    if select_response:
        return success_json(records=select_response)
    return failure_json(message="No Records Found", status_code=S_NOTFOUND_CODE)


@router.delete("/users")
@authorize_token
async def delete_library_user(request: Request, user_id, library_id,
                              token: HTTPAuthorizationCredentials = Depends(security)):
    select_relation = select_query(table_name=S_LIBRARY_USER_TABLE,
                                   conditions={"library_id": library_id, "user_id": user_id})
    if not select_relation:
        return failure_json(message="User Not in Library.", status_code=S_NOTFOUND_CODE)

    response = delete_query(table_name=S_LIBRARY_USER_TABLE, record_id=select_relation[0]["id"])[0]
    if response["status_bool"]:
        return success_json(records=[], message=f"User Deleted from Library - [{library_id}]")
    return failure_json(message="Something Went Wrong", status_code=S_BADREQUEST_CODE)
