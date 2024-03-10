from fastapi import FastAPI, Depends, HTTPException, Request

# from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import JWTError
from datetime import datetime
# import json

# import asyncpg
import socketio
from models import Room

from utils.db_util import lifespan, db
from utils.auth_util import create_jwt_token, check_jwt_token
from services.db_service import (
    check_user_exists,
    get_messages,
    save_message,
    user_exists_in_room,
    get_user,
    insert_room,
    insert_user_room_mapping,
    get_user_rooms,
    # get_all_user_room_mappings
)

# FastAPI application
app = FastAPI(lifespan=lifespan)


@app.post("/token")
@app.post("/login")
async def login(request: Request):
    print("GOT LOGIN REQUEST:", request)
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


@app.get("/whoami")
async def whoami(
    current_user: str = Depends(check_jwt_token),
):
    return {"username": current_user}


@app.post("/create_chat_room")
async def create_room(room: Room, username: str = Depends(check_jwt_token)):
    transaction = await db.transaction()
    try:
        # create a room
        room_id = await insert_room(db, room.name)
        # Add the user to the room
        await insert_user_room_mapping(db, username, room_id)
        # Add the rest of the users to the room
        for user in room.users:
            exists = await check_user_exists(db, user)
            if exists:
                await insert_user_room_mapping(db, user, room_id)
    except Exception as e:
        print("an error occurred", e)
        await transaction.rollback()
        return HTTPException(status_code=400, detail="Failed to create chat room")
    else:
        await transaction.commit()
        return JSONResponse(
            {"message": "A room has been created.", "room_id": room_id}, status_code=200
        )


sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
sio.background_task_started = False

# wrap with ASGI application
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)


@sio.on("connect")
async def connect(sid, env):
    # print("THIS IS THE ENV:", env)
    print("new client connected with session id: " + str(sid))

    """Apparently socketio does automatically send a "connect" event on succesful connect so this isn't needed"""
    # payload = {"successful": True, "description": "Connection successful"}
    # await sio.emit("connect_ack", payload, to=sid)


@sio.on("authenticate")
async def authenticate(sid, token):
    if token is None:
        raise HTTPException(status_code=400, detail="Missing token")

    # Validate the token and add the username to the user session.
    try:
        username = check_jwt_token(token)
        print(f"Authenticate received session token: {token}")

        """
        A user is authenticated if their username is in the session["username"].
        In the future, the username should be accessed through this.
        """
        async with sio.session(sid) as session:
            print("In sio session section")
            session["username"] = username
            payload = {"successful": True, "description": "Authentication successful"}
            await sio.emit("authenticate_ack", payload, to=sid)
            print(f"Connection has been made with the user: {username}")

            # Register sid to rooms that the user already is a prt of
            user_rooms = await get_user_rooms(db, username)
            print("Registering user to rooms:", user_rooms)
            for mapping in user_rooms:
                await sio.enter_room(sid, mapping["room_id"])
            print("Done in authenticate")

            print("Background task has been started:", sio.background_task_started)
            # Start a scheduled task
            if not sio.background_task_started:
                sio.start_background_task(scheduled_ping)
                sio.background_task_started = True

    except JWTError as e:
        payload = {"successful": False, "description": "Authentication failed"}
        await sio.emit("authenticate_ack", payload, to=sid)
        print(f"Authentication JWTError: {e}")

    except Exception as e:
        payload = {"successful": False, "description": "Authentication failed"}
        await sio.emit("authenticate_ack", payload, to=sid)
        print(f"Unknown error in authenticate {e}")


@sio.on("join_room")
async def join_room(sid, room_id):
    try:
        print("join_room sid", sid)
        print("join_room room_id", room_id)
        room_id = int(room_id)
        async with sio.session(sid) as session:
            username = session["username"]
            if not await user_exists_in_room(db, username, room_id):
                raise Exception("No permission to join the room")

        await sio.enter_room(sid, room_id)
        payload = {"successful": True, "description": "Room joined succesfully"}
        await sio.emit("join_room_ack", payload, to=sid)

    except ValueError:
        payload = {"successful": False, "description": "Invalid room ID"}
        await sio.emit("join_room_ack", payload, to=sid)

    except KeyError:
        payload = {"successful": False, "description": "No username found in session"}
        await sio.emit("join_room_ack", payload, to=sid)

    except Exception as e:
        print(f"Exception occurred while joining a room: {e}")
        payload = {"successful": False, "description": "Error occurred while joining a room"}
        await sio.emit("join_room_ack", payload, to=sid)


@sio.on("get_user_rooms")
async def get_user_chats(sid, _=None):
    print("get_user_rooms sid:", sid)
    async with sio.session(sid) as session:
        username = session["username"]
        rooms = await get_user_rooms(db=db, username=username)
        print("ROOMS:", rooms)
        await sio.emit("return_user_rooms", rooms, to=sid)


@sio.on("fetch_room_messages")
async def fetch_room_messages(sid, room_id):
    print("fetch_room_messages room_id", room_id)
    room_id = int(room_id)

    async with sio.session(sid) as session:
        username = session["username"]
        print("Session username:", username)
        if not await user_exists_in_room(db, username, room_id):
            print("User not in room")
            payload = {"successful": False, "description": "User is not in the room"}
            await sio.emit("fetch_room_messages_response", payload, to=sid)
            raise Exception("No permission to join the room")

        messages = await get_messages(db, room_id)
        payload = {
            "successful": True,
            "description": "",
            "messages": messages
        }

        print(messages)
        await sio.emit("fetch_room_messages_response", payload, to=sid)


@sio.on("send_msg")
async def send_message(sid, message, room_id):
    try:
        print(f"send_message called {message} to room id: {room_id}")
        room_id = int(room_id)

        # Get the user name from the session
        session = await sio.get_session(sid)
        username = session["username"]

        if not await user_exists_in_room(db, username, room_id):
            payload = {
                "successful": False,
                "description": "User is not in the room",
                "data": None
            }
            await sio.emit("receive_msg", data=payload, to=sid)
            raise Exception("no permission to send messages to the room")

        # Save the message
        await save_message(db, username, room_id, message)
        print("Message has been saved")

        # Prepare data to emit
        data = {
            "username": username,
            "message": message,
            "timestamp": str(datetime.now()),
            "message_id": 10,  # This needs to be fetched from the database with the save_message function
        }

        payload = {
            "successful": True,
            "description": "",
            "data": data,
            "room_id": room_id
        }

        print("Sending payload", payload)

        # Emit the message to the room
        await sio.emit("receive_msg", data=payload, room=room_id)
        # print("Sent payload")

    except ValueError as ve:
        print(f"ValueError: {ve}")

    except JWTError as e:
        print(f"JWT ERROR: {e}")

    except Exception as e:
        print(f"Exception occurred while sending message: {e}")


@sio.on("test_download")
async def test_download(sid, _):
    binary_payload = 0
    for i in range(1024):
        if i % 2 == 1:
            binary_payload |= 1 << i

    start_time = datetime.now()
    end_time = datetime.now()
    packets_sent = 0
    # For future, grow the payload size based on connection speed to reduce the effect of latency.
    print("Starting download")
    while (end_time - start_time).total_seconds() < 10:  # Do for 10 seconds
        await sio.emit("receive_throughput", data=binary_payload, to=sid)
        packets_sent += 1
        end_time = datetime.now()

    throughput_kbps = (packets_sent * 1024) / (end_time - start_time).total_seconds()

    print("GOT THROUGHPUT:", throughput_kbps)

    await sio.emit("throughput_download_result", data=throughput_kbps, to=sid)


# For the throughput tests, using socketio.SimpleClient.call can be used to wait for the messages to be sent
# The basic emit doesn't wait for the message to be received.

# client_total_bytes = {}

# @sio.on("test_upload")
# async def test_upload(sid):
#     total = 0


# @sio.on("test_latency")
# async def test_latency(sid, timestamp):


@sio.on("disconnect")
async def disconnect(sid):
    print("client disconnected: " + str(sid))


# async def add_users_to_rooms():
#     mapping = await get_all_user_room_mappings(db)
#     print("ROOMS:", mapping)

@sio.on("ping_ack")
async def ping_ack(sid, time_string):
    # print("Received ping_ack with time:", time_string)
    current_time = datetime.now()
    ack_time = datetime.fromisoformat(time_string)

    # Returns the time difference in milliseconds
    time_difference = int((current_time - ack_time).total_seconds() * 1000)

    # print("Emitting time difference")

    await sio.emit("ping_result", time_difference, to=sid)


async def scheduled_ping():
    # print("IN SCHEDULED TASK!!")
    while True:
        # print("Waiting for 10 sec and sending ping")
        await sio.sleep(10)
        payload = str(datetime.now())
        print("Emitting payload:", payload)
        await sio.emit("ping", payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
