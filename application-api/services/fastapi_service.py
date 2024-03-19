from fastapi import APIRouter, Depends, HTTPException, Request, Response  # noqa

# from models import Room
from utils.db_util import db
from utils.auth_util import create_jwt_token, check_jwt_token
from services.db_service import get_user

router = APIRouter()


@router.post("/token")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    except Exception:
        raise HTTPException(status_code=400, detail="Payload not valid JSON")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing username or password")
    if not await get_user(db, username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"token_type": "bearer", "token": create_jwt_token(data={"sub": username})}


@router.get("/throughput_download")
async def download(request: Request, username: str = Depends(check_jwt_token)):
    # Raise an exception if jwt is invalid
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the requested size from the payload
    try:
        size_kb = int(request.query_params.get("size_kb", 1))
    except Exception:
        raise HTTPException(status_code=400, detail="Integer url parameter size_kb is required.")

    print("DOWNLOAD SIZE:", size_kb)

    if size_kb > 10_000_000:
        raise HTTPException(
            status_code=400, detail="Requested size exceeds the limit (10 GB)"
        )

    # Generate data of the requested size
    data = b"A" * (size_kb * 1024)  # 1 KB = 1024 bytes

    return Response(content=data, media_type="application/octet-stream")


@router.post("/throughput_upload")
async def upload(request: Request, username: str = Depends(check_jwt_token)):
    # Raise an exception if jwt is invalid
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the requested size from the payload
    bytes_received = await request.body()

    payload_json = {"payload": len(bytes_received)}

    return payload_json
