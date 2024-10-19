from fastapi import APIRouter, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from db_helper import *
from om_helper import *

import pyotp
from datetime import timedelta
from email_helper import send_otp_email

router = APIRouter(tags=["otp"])


@router.get("/generate_otp")
@authorize_token
async def generate_otp(user_email: str):
    otp_secret = pyotp.random_base32()
    totp = pyotp.TOTP(otp_secret)
    otp = totp.now()

    response = select_query(table_name=S_USER_TABLE, conditions={"user_email": user_email})
    if response:
        otp_expiry = datetime.now() + timedelta(minutes=OTP_VALID_TIME)
        result = update_query(table_name=S_USER_TABLE, conditions={"user_email": user_email},
                              data={"user_otp": otp, "otp_expiry": otp_expiry})
        result = result[0]
        send_otp_email(to_email=user_email, otp_code=otp)
        records = result.get("records")
        return success_json(records=records)
    return failure_json(message="User Not Found in DB", status_code=S_NOTFOUND_CODE)


@router.get("/validate_otp")
@authorize_token
async def validate_otp(user_email: str, otp: str):
    select_response = select_query(table_name=S_USER_TABLE, conditions={"user_email": user_email})
    if select_response:
        select_response = select_response[0]
        valid_time = parse_timestamp(str_timestamp=select_response["otp_expiry"])
        present_time = datetime.now()

        if select_response["user_otp"] != otp:
            return failure_json(message="Invalid OTP", status_code=S_BADREQUEST_CODE)
        elif select_response["user_otp"] == otp and present_time > valid_time:
            return failure_json(message="OTP Expired, Invalid OTP", status_code=S_BADREQUEST_CODE)
        elif select_response["user_otp"] == otp and present_time < valid_time:
            records = [{"token": create_access_token(user_name=select_response["user_name"], expires_time=2629743)}]
            return success_json(records=records, message="Valid OTP")
    return failure_json(message="User Not Found in DB", status_code=S_NOTFOUND_CODE)


@router.get("/login")
async def login(email: str, password: str):
    condition = {"user_email": email}
    select_response = select_query(table_name=S_USER_TABLE, conditions=condition)
    if select_response:
        select_response = select_response[0]
        user_id = select_response["id"]
        if select_response["status"] != "active":
            return failure_json(message="User Not Allowed", status_code=S_FORBIDDEN_CODE)
        if select_response["user_password"] == password:
            update_query(table_name=S_USER_TABLE, conditions={'id': user_id}, data={"user_checkin": True})
            records = [{"token": create_access_token(user_name=select_response["user_name"], expires_time=2629743),
                        "user_id": user_id}]
            return success_json(records=records, message="Successfully logged in")


@router.get("/check_in")
@authorize_token
async def check_in(email: str, password: str):
    condition = {"user_email": email}
    select_response = select_query(table_name=S_USER_TABLE, conditions=condition)
    if select_response:
        select_response = select_response[0]
        user_id = select_response["id"]
        if select_response["status"] != "active":
            return failure_json(message="User Cannot Check In, Membership Expired", status_code=S_FORBIDDEN_CODE)

        if select_response["user_checkin"]:
            return failure_json(message="User is already checked-in", status_code=S_BADREQUEST_CODE)

        if select_response["user_password"] == password:
            update_query(table_name=S_USER_TABLE, conditions={'id': user_id}, data={"user_checkin": True})
            records = [{"token": create_access_token(user_name=select_response["user_name"], expires_time=2629743),
                        "user_id": user_id}]
            return success_json(records=records, message="Checked In")

        return failure_json(message="Incorrect Password", status_code=S_BADREQUEST_CODE)

    return failure_json(message="User Not Found or Incorrect Email_ID", status_code=S_NOTFOUND_CODE)


@router.get("/check_out")
@authorize_token
async def check_out(user_id: int):
    condition = {"id": user_id}
    select_response = select_query(table_name=S_USER_TABLE, conditions=condition)
    if select_response:
        select_response = select_response[0]
    if not select_response["user_checkin"]:
        return failure_json(message="User not checked-in", status_code=S_BADREQUEST_CODE)
    penalty_response = select_query(table_name=S_RENTAL_PENALTY_VIEW, conditions={"user_id": user_id})
    if penalty_response:
        return failure_json(message="Clear Penalties, To Generate Outpass", status_code=S_FORBIDDEN_CODE)
    update_query(table_name=S_USER_TABLE, conditions={'id': user_id}, data={"user_checkin": False})
    return success_json(records=[], message="Checked Out")
