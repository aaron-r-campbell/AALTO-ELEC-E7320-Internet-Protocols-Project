from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
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

list_of_active_users = []


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

async def insert_room(room_name: str) -> int:
    query = "INSERT INTO rooms(name) VALUES (:name) RETURNING id"
    values = {"name": room_name}
    room_id = await database.execute(query=query, values=values)
    return room_id

async def insert_user_room_mapping(user_name: str, room_id: int) -> None:
    query = "INSERT INTO user_room_mappings(user_name, room_id) VALUES (:user_name, :room_id)"
    values = {"user_name": user_name, "room_id": room_id}
    await database.execute(query=query, values=values)

async def check_user_exists(username: str) -> bool:
    query="SELECT * FROM users WHERE name = :username",
    values = {"username": username}
    response = await database.execute(query=query, values=values)
    print(response)
    return bool(response)

@app.post("/login")
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
    user = await database.fetch_one(
        query="SELECT * FROM users WHERE name = :username AND password = :password",
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


@app.post("/create_chat_room")
async def create_room(request: Request, user_name: str = Depends(check_jwt_token)):
    try:
        data = await request.json()
        room_name = data.get("room_name")
        users = data.get("users")

        async with database.transaction():
            room_id = await insert_room(room_name)
            await insert_user_room_mapping(user_name, room_id)
            for user in users:
                if check_user_exists(user):
                    await insert_user_room_mapping(user, room_id)

        return JSONResponse({"message": f"A room with {room_id} has been created.", "room_id": room_id}, status_code=200)
    except Exception as e:
        print("an error occured", e)
        return HTTPException(status_code=400, detail="Failed to create chat room")

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

# wrap with ASGI application
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)


@sio.on("connect")
async def connect(sid, env):
    # print("new client connected with session id: " + str(sid))

    query_args = {key: value for key, value in (pair.split("=") for pair in str(env.get("QUERY_STRING")).split("&"))}

    if "token" not in query_args:
        raise HTTPException(status_code=400, detail="Missing token")

    token = query_args["token"]
    check_jwt_token(token)

    print(f"Received session token: {token}")

@sio.on("message")
async def message(sid, data):
    print(f"received message: {data}")
    await sio.emit('message', {'data': 'foobar'})

@sio.on("join_room")
async def join_room(sid, token, room_id):
    try:
        username = check_jwt_token(token)
        #1. CheckUserExistsInRoom
        sid.enter_room(sid, room_id)
    except JWTError:
        sid.emit("error", "not a valid user")
    except Exception as e:
        sid.emit("error", "error occured while joining a room")

@sio.on("disconnect")
async def disconnect(sid):
    print("client disconnected: " + str(sid))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
