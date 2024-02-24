from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from databases import Database
from dotenv import load_dotenv
# import asyncpg
import os
from contextlib import asynccontextmanager
import socketio

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Secret key to sign JWT token
SECRET_KEY = os.getenv("SECRET_KEY")
ENCRYPTION_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Create a connection to the PostgreSQL database
database = Database(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to db on startup
    await database.connect()
    yield
    # Disconnect from db on shutdown
    await database.disconnect()


# FastAPI application
app = FastAPI(lifespan=lifespan)

# OAuth2PasswordBearer for handling token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ENCRYPTION_ALGORITHM)
    return encoded_jwt


def check_jwt_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ENCRYPTION_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    # Execute the SQL query using databases
    user = await database.fetch_one(
        query="SELECT * FROM users WHERE username = :username AND password = :password",
        values={"username": username, "password": password},
    )

    if user:
        expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_jwt_token(data={"sub": username}, expires_delta=expires)
        return {"token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/whoami")
async def whoami(current_user: str = Depends(check_jwt_token)):
    return {"username": current_user}

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

# wrap with ASGI application
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)


@sio.on("connect")
async def connect(sid, env):
    print("new client connected with session id: " + str(sid))


@sio.on("message")
async def message(sid, data):
    print(f"received message: {data}")
    await sio.emit('message', {'data': 'foobar'})


@sio.on("disconnect")
async def disconnect(sid):
    print("client disconnected: " + str(sid))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
