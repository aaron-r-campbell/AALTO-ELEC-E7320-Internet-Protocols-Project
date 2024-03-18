from fastapi import FastAPI, Depends, HTTPException, Request, Response  # noqa

# from models import Room
from utils.db_util import db
from utils.auth_util import create_jwt_token, check_jwt_token
from services.db_service import get_user


def setup(app: FastAPI):
    @app.post("/token")
    async def login(request: Request):
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Payload not valid JSON")

        username = data.get("username")
        password = data.get("password")

        if not username:
            raise HTTPException(status_code=400, detail="Missing username")
        if not password:
            raise HTTPException(status_code=400, detail="Missing password")

        # Execute the SQL query using databases
        user = await get_user(db, username, password)

        if user:
            return {
                "token_type": "bearer",
                "token": create_jwt_token(data={"sub": username}),
            }
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # TODO: Add authentication
    @app.get("/throughput_download")
    async def download(request: Request, username: str = Depends(check_jwt_token)):
        # Extract the requested size from the payload
        try:
            size_kb = int(request.query_params.get("size_kb", 1))
        except Exception:
            raise HTTPException(status_code=400, detail="Unknown error")

        print("DOWNLOAD SIZE:", size_kb)

        if size_kb > 10_000_000:
            raise HTTPException(
                status_code=400, detail="Requested size exceeds the limit (10 GB)"
            )

        # Generate data of the requested size
        data = b"A" * (size_kb * 1024)  # 1 KB = 1024 bytes

        return Response(content=data, media_type="application/octet-stream")

    # TODO: Add authentication
    @app.post("/throughput_upload")
    async def upload(request: Request, username: str = Depends(check_jwt_token)):
        # Extract the requested size from the payload
        bytes_received = await request.body()

        payload_json = {"payload": len(bytes_received)}

        return payload_json
