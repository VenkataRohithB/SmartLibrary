from constants import SECRET_KEY, S_BADREQUEST_CODE
from om_helper import *
from fastapi import APIRouter, FastAPI

router = APIRouter(tags=["auth"])
# router = FastAPI()


@router.get("/generate_token")
async def token_generation(user_name: str, passcode: str, expiry: int = None):
    if passcode != SECRET_KEY:
        return failure_json(message="INVALID PASSCODE...!", status_code=S_BADREQUEST_CODE)

    token = {"token": create_access_token(user_name=user_name, expires_time=expiry)}
    return success_json(records=[token], message="Generated new token successfully")


@router.get("/validate_token")
async def token_validation(token: str):
    try:
        if validate_token(token=token):
            return success_json(records=[], message="Token is valid")
        else:
            return failure_json(message="Token is invalid or expired", status_code=401)
    except Exception as e:
        return failure_json(message="Token is invalid", status_code=401)

