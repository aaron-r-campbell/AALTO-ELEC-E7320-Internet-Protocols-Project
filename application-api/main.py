from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
# import asyncpg
import os
import socketio
from db_queries import check_user_exists, get_messages, save_message, user_exists_in_room, get_user, insert_room, insert_user_room_mapping, lifespan, database  # noqa -- Removes local linter warning :)
from models import Room

# Secret key to sign JWT token
SECRET_KEY = os.getenv("SECRET_KEY")
ENCRYPTION_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

list_of_active_users = []

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
    user = await get_user(username, password)

    if user:
        expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_jwt_token(data={"sub": username}, expires_delta=expires)
        return {"token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/whoami")
async def whoami(current_user: str = Depends(check_jwt_token)):
    return {"username": current_user}


@app.post("/create_chat_room")
async def create_room(room: Room, username: str = Depends(check_jwt_token)):
    transaction = await database.transaction()
    try:
        # create a room
        room_id = await insert_room(room.name)
        # Add the user to the room
        await insert_user_room_mapping(username, room_id)
        # Add the rest of the users to the room
        for user in room.users:
            exists = await check_user_exists(user)
            if exists:
                await insert_user_room_mapping(user, room_id)
    except Exception as e:
        print("an error occured", e)
        await transaction.rollback()
        return HTTPException(status_code=400, detail="Failed to create chat room")
    else:
        await transaction.commit()
        return JSONResponse({"message": "A room has been created.", "room_id": room_id}, status_code=200)


@app.get("/messages")
async def retrieve_messages(room_id: int, username: str = Depends(check_jwt_token)):
    try:
        if await user_exists_in_room(username, room_id):
            messages = await get_messages(room_id)
            print(messages)
            return JSONResponse({"messages": json.dumps(messages)}, status_code=200)
    except Exception as e:
        print(f"an error occured while retrieveing messages: {e}")
        return HTTPException(status_code=500)

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

    # Validate the token and add the username to the user session.
    token = query_args["token"]
    username = check_jwt_token(token)
    async with sio.session(sid) as session:
        session['username'] = username
    print(f"Conenection has been made with the user: {username}")
    print(f"Received session token: {token}")


@sio.on("message")
async def message(sid, data):
    print(f"received message: {data}")
    await sio.emit('message', {'data': 'foobar'})


@sio.on("join_room")
async def join_room(sid, room_id):
    try:
        room_id = int(room_id)
        async with sio.session(sid) as session:
            username = session['username']
            if not await user_exists_in_room(username, room_id):
                raise Exception("No permission to join the room")

        await sio.enter_room(sid, room_id)
        await sio.emit('join_room', 'You have joined the room successfully', room=sid)

    except ValueError:
        await sio.emit("error", "Invalid room ID")

    except KeyError:
        await sio.emit("error", "No username found in session")

    except Exception as e:
        print(f"Exception occurred while joining a room: {e}")
        await sio.emit("error", "Error occurred while joining a room")


@sio.on("send_msg")
async def send_message(sid, message, room_id):
    try:
        print(f"send_message called {message} to room id: {room_id}")
        room_id = int(room_id)

        # Get the user name from the session
        session = await sio.get_session(sid)
        username = session['username']

        if not await user_exists_in_room(username, room_id):
            raise Exception("no permission to send messages to the room")

        # Save the message
        await save_message(sender_name=username, room_id=room_id, message=message)
        print("Message has been saved")

        # Prepare data to emit
        data = {"username": username, "message": message}

        # Emit the message to the room
        await sio.emit("receive_msg", data=data, room=room_id, skip_sid=sid)

    except ValueError as ve:
        print(f"ValueError: {ve}")

    except JWTError as e:
        print(f"JWT ERROR: {e}")

    except Exception as e:
        print(f"Exception occured while sending message: {e}")


@sio.on("test_download")
async def test_throughput(sid):
    binary_payload = 0
    for i in range(1024):
        if i % 2 == 1:
            binary_payload |= 1 << i

    start_time = datetime.now()
    end_time = datetime.now()
    packets_sent = 0
    while (end_time - start_time).total_seconds() < 10:  # Do for 10 seconds
        await sio.emit("receive_throughput", data=binary_payload, to=sid)
        packets_sent += 1
        end_time = datetime.now()

    throughput_kbps = (packets_sent * 1024) / (end_time - start_time).total_seconds()

    await sio.emit("throughput_download_result", data=throughput_kbps, to=sid)


@sio.on("disconnect")
async def disconnect(sid):
    print("client disconnected: " + str(sid))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
