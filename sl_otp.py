from fastapi import APIRouter, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta, datetime

from db_helper import *
from om_helper import *
from email_helper import send_otp_email
import pyotp

router = APIRouter(tags=["otp"])


@router.get("/generate_otp",
            summary="Generate OTP",
            description="Generates a One-Time Password (OTP) for user email verification. "
                        "Sends the OTP to the user's email and stores it in the database.")
@authorize_token
async def generate_otp(request: Request, user_email: str, token: HTTPAuthorizationCredentials = Depends(security)):
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


@router.get("/validate_otp",
            summary="Validate OTP",
            description="Validates the OTP provided by the user. "
                        "Checks if the OTP is correct and if it has expired.")
@authorize_token
async def validate_otp(request: Request, user_email: str, otp: str, token: HTTPAuthorizationCredentials = Depends(security)):
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


@router.get("/login",
            summary="User Login",
            description="Logs in the user with their email and password. "
                        "If successful, returns a token and user ID.")
async def login(user_email: str, password: str):
    condition = {"user_email": user_email}
    select_response = select_query(table_name=S_USER_TABLE, conditions=condition)

    if select_response:
        select_response = select_response[0]
        user_id = select_response["id"]
        if select_response["status"] != "active":
            return failure_json(message="User Not Allowed", status_code=S_FORBIDDEN_CODE)
        if select_response["user_password"] == password:
            otp_secret = pyotp.random_base32()
            totp = pyotp.TOTP(otp_secret)
            otp = totp.now()

            send_otp_email(to_email=user_email, otp_code=otp)
            update_query(table_name=S_USER_TABLE, conditions={"user_email": user_email},
                         data={"user_otp": otp, "otp_expiry": OTP_VALID_TIME})

            update_query(table_name=S_USER_TABLE, conditions={'id': user_id}, data={"user_checkin": True})
            records = [{"token": create_access_token(user_id=select_response["id"], expires_time=2629743),
                        "user_id": user_id}]
            return success_json(records=records, message="Successfully logged in")


@router.get("/validate_pass", summary="Verifies Check-In and Out Pass",
            description="Generally used by library QR Scanner where it verifies & validates the pass")
@authorize_token
async def validate_pass(request: Request, code, token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token_response = validate_token(code)
        token_response = token_response["payload"]
        user_id = token_response["user_id"]
        meta_data = token_response["meta_data"]

        select_response = select_query(table_name=S_USER_TABLE, conditions={"id": user_id})
        if not select_response:
            return failure_json(message="User Not Found", status_code=S_NOTFOUND_CODE)

        if meta_data == "check_in":
            select_response = select_response[0]
            if select_response["status"] != "active":
                return failure_json(message="Membership Expired, User Cannot Check-IN",
                                    status_code=S_FORBIDDEN_CODE)

            if select_response["user_checkin"]:
                return failure_json(message="User already Checked-IN", status_code=S_BADREQUEST_CODE)
            update_query(table_name=S_USER_TABLE, conditions={'id': user_id}, data={"user_checkin": True})
            return success_json(records=select_query(table_name=S_USER_TABLE, conditions={"id": user_id}), message="User Verified")

        elif meta_data == "check-out":
            select_response = select_response[0]
            if not select_response["user_checkin"]:
                return failure_json(message="User not checked-in", status_code=S_BADREQUEST_CODE)

            rental_details = select_query(table_name=S_RENTAL_VIEW, conditions={"user_id": user_id, "status": "active"})
            if rental_details:
                if len(rental_details) > S_USER_BOOK_LIMIT:
                    return failure_json(message=f"User Cannot Return More Than: [{S_USER_BOOK_LIMIT}] Books",
                                        status_code=S_BADREQUEST_CODE)

            penalty_response = select_query(table_name=S_RENTAL_PENALTY_VIEW, conditions={"user_id": user_id})
            if penalty_response:
                return failure_json(message="Pending Penalties", status_code=S_FORBIDDEN_CODE)

            update_query(table_name=S_USER_TABLE, conditions={'id': user_id}, data={"user_checkin": False})
            return success_json(records=select_query(table_name=S_USER_TABLE, conditions={"id": user_id}), message="User Verified")
        return failure_json(message="Invalid Pass", status_code=S_BADREQUEST_CODE)

    except JWTError as e:
        return failure_json(message="Invalid Pass", status_code=S_BADREQUEST_CODE)


@router.get("/check_in_code", summary="User Check-In Pass Generation",
            description="Generates Check-In Pass for the user by verifying their membership validity. ")
@authorize_token
async def check_in_code(request: Request, user_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    select_response = select_query(table_name=S_USER_TABLE, conditions={"id": user_id})
    if not select_response:
        return failure_json(message="User Not Found", status_code=S_NOTFOUND_CODE)

    select_response = select_response[0]
    if select_response["status"] != "active":
        return failure_json(message="Cannot Generate Check-In Pass, Membership Expired",
                            status_code=S_FORBIDDEN_CODE)

    if select_response["user_checkin"]:
        return failure_json(message="User already Checked-in", status_code=S_BADREQUEST_CODE)

    records = [
        {"token": create_access_token(user_id=select_response["id"], meta_data="check_in", expires_time=300)}]
    return success_json(records=records, message="In-Pass Generated")


@router.get("/check_out", summary="User Check-Out Pass Generation",
            description="Generates Check-Out Pass for the user, ensuring they have no outstanding penalties or excessive rentals.")
@authorize_token
async def check_out(request: Request, user_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    select_response = select_query(table_name=S_USER_TABLE, conditions={"id": user_id})
    if not select_response:
        return failure_json(message="User Not Found", status_code=S_NOTFOUND_CODE)
    select_response = select_response[0]
    if not select_response["user_checkin"]:
        return failure_json(message="User not checked-in", status_code=S_BADREQUEST_CODE)

    rental_details = select_query(table_name=S_RENTAL_VIEW, conditions={"user_id": user_id, "status": "active"})
    if rental_details:
        if len(rental_details) > S_USER_BOOK_LIMIT:
            return failure_json(message=f"User Cannot Return More Than: [{S_USER_BOOK_LIMIT}] Books",
                                status_code=S_BADREQUEST_CODE)

    penalty_response = select_query(table_name=S_RENTAL_PENALTY_VIEW, conditions={"user_id": user_id})
    if penalty_response:
        return failure_json(message="Clear Penalties, To Generate Outpass", status_code=S_FORBIDDEN_CODE)

    return success_json(records=[{"token": create_access_token(user_id=select_response["id"], meta_data="check-out", expires_time=300)}], message="Out-Pass, Generated")
