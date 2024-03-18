from fastapi import FastAPI, Depends, HTTPException, Request, Response  # noqa

# from fastapi.security import OAuth2PasswordBearer
# from fastapi.responses import JSONResponse
from jose import JWTError
from datetime import datetime
import json

# import asyncpg
import socketio
# from models import Room
from typing import Dict, List
from models.data import DocumentItem
from utils.db_util import lifespan, db
from utils.auth_util import create_jwt_token, check_jwt_token
from services.db_service import (
    check_user_exists,
    get_messages,
    save_message,
    user_exists_in_room,
    get_user,
    get_user_rooms,
    get_all_users,
    set_user_activity,
    add_user_to_chat_room,
    get_usernames_not_in_room,
    create_chat_room,
    save_file,
    get_file,
    check_roomid_exists,
    # get_roomname_by_id,
    delete_room_by_id,
)

# FastAPI application
app = FastAPI(lifespan=lifespan)


@app.post("/token")
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
        raise HTTPException(status_code=400, detail="Requested size exceeds the limit (10 GB)")

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


sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
sio.background_task_started = False

# wrap with ASGI application
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

# Mapping from usernames to sids.
# Is needed for inviting other users to a chatroom
user_sockets_mapping: Dict[str, str] = {}


@sio.on("connect")
async def connect(sid, env):
    """Apparently socketio does automatically send a "connect" event on succesful connect so this isn't needed"""


@sio.on("authenticate")
async def authenticate(sid, token):
    try:
        # TODO: This throws an HTTPException, which needs to be handled in the error cases
        username = check_jwt_token(token)
        print(f"Authenticate received session token: {token}")

        """
        A user is authenticated if their username is in the session["username"].
        In the future, the username should be accessed through this.
        """
        async with sio.session(sid) as session:
            # print("In sio session section")
            session["username"] = username

            user_sockets_mapping[username] = sid

            # TODO: IDK what error this throws but should be handled. Currently goes to
            async with db.transaction():
                # Get rooms that user is in to register user to receive messages from them
                user_rooms = await get_user_rooms(db, username)

                # Update the user's active status in the database
                await set_user_activity(db, username, True)

                # fetch the list of users to inform that activity has changed
                users = await get_all_users(db)

            # Register sid to rooms that the user already is a part of
            for mapping in user_rooms:
                await sio.enter_room(sid, mapping["room_id"])

            # TODO: Add successful, description, payload as arguments, not as payload
            payload = {"successful": True, "description": "Authentication successful"}
            await sio.emit("authenticate_ack", payload, to=sid)

            # Send user activities of all users to the connecting user
            # TODO: Add successful, description, payload
            await sio.emit("user_activities", users, to=sid)

            # Inform all users of the activity of the connecting user
            # TODO: Add successful, description, payload
            user_update_payload = {"username": username, "active": True}
            await sio.emit("user_activities_update", user_update_payload, skip_sid=sid)

            # Send initiol ping just to display ping instantly
            payload = str(datetime.now())
            await sio.emit("ping", payload)

            if not sio.background_task_started:
                # Start scheduled pings
                sio.start_background_task(scheduled_ping)
                sio.background_task_started = True

    except HTTPException as e:
        payload = {"successful": False, "description": "Authentication failed"}
        await sio.emit("authenticate_ack", payload, to=sid)
        print(f"Authentication HTTPException: {e}")

    except JWTError as e:
        payload = {"successful": False, "description": "Authentication failed"}
        # TODO: await sio.emit("authenticate_ack", data=(succesful=false, description="autherror", payload=None), to=sid)  # noqa
        await sio.emit("authenticate_ack", payload, to=sid)
        print(f"Authentication JWTError: {e}")

    except Exception as e:
        payload = {"successful": False, "description": "Authentication failed"}
        # TODO: await sio.emit("authenticate_ack", data=(succesful=false, description="autherror", payload=None), to=sid)  # noqa
        await sio.emit("authenticate_ack", payload, to=sid)
        print(f"Unknown error in authenticate {e}")


@sio.on("remove_room")
async def remove_room(sid, room_id):
    async with sio.session(sid) as session:

        # For checking if the user is authenticated
        username = session["username"]  # noqa

        async with db.transaction():

            print("Here1")

            if not await check_roomid_exists(db, room_id):
                await sio.emit("remove_room_response", data=(False, "Room does not exist", None), to=sid)
                print("Here1.5")
                raise ValueError(f"Unknown room id: {room_id}")

            print("Here2")

            await delete_room_by_id(db, room_id)

            print("Here3")

            await sio.emit("remove_room_response", data=(True, "", room_id), room=room_id)
            print("Here3.5")
            await sio.close_room(room_id)
            print("Here4")


@sio.on("create_room")
async def create_room(sid, room_name):

    # TODO: Refactor both assertions to have error handling: emit a message to "return_user_rooms" event with:
    # sio.emit("return_user_rooms", data=(false, "autherror", None), to=sid)
    if not isinstance(room_name, str):
        payload = {
            "successful": False,
            "description": "Room_name is not a string",
            "payload": None
        }
        await sio.emit("return_user_rooms", payload, to=sid)
        raise Exception("Room_name is not a string")

    if len(room_name) < 3:
        payload = {
            "successful": False,
            "description": "Room_name is not long enough",
            "payload": None
        }
        await sio.emit("return_user_rooms", payload, to=sid)
        raise Exception("Room_name is not long enough")

    # This does allow repeat room names!!!
    async with sio.session(sid) as session:
        # TODO: Error if username doesn't exist
        username = session["username"]

        # create a room
        room_id = await create_chat_room(db, room_name, username)

        # Add the creator to the sio room so they receive messages there
        await sio.enter_room(sid, room_id)

        # Retrieves all users for the currrent user
        rooms = await get_user_rooms(db=db, username=username)
        payload = {
            "successful": True,
            "description": "",
            "payload": rooms
        }

        # Update the room list of the creator
        # TODO: await sio.emit("return_user_rooms", data=(succesful, description, rooms), to=sid)
        await sio.emit("return_user_rooms", payload, to=sid)


@sio.on("get_users_not_in_room")
async def get_users_not_in_room(sid, room_id):
    print(f"{sid} is retrieving users for {room_id}")
    room_id = int(room_id)
    async with sio.session(sid) as session:
        # TODO: Error if username doesn't exist
        username = session["username"]

        # Inviter has to be in the room
        if not await user_exists_in_room(db, username, room_id):
            payload = {"successful": False, "description": "Authentication failed"}
            await sio.emit("get_users_not_in_room_response", payload, to=sid)
            raise Exception("No permission to join the room")
    usernames = await get_usernames_not_in_room(db, room_id)

    payload = {
        "successful": True,
        "data": usernames,
        "description": ""
        }

    print("Retrieved users:", payload)

    # TODO: Change from payload containing everything to
    # sio.emit("get_users_not_in_room_response", data=(successful, description, payload), to=sid)
    await sio.emit("get_users_not_in_room_response", payload, to=sid)


@sio.on("add_to_room")
async def add_to_room(sid, room_id, new_user):
    try:
        print("add_to_room", sid, room_id, new_user)
        room_id = int(room_id)

        async with db.transaction():

            if not await check_user_exists(db, new_user):
                payload = {"successful": False, "description": "New user does not exist"}
                await sio.emit("add_to_room_response", payload, to=sid)
                raise Exception("New user does not exist")

            async with sio.session(sid) as session:
                # TODO: Error if username doesn't exist
                username = session["username"]

                # Inviter has to be in the room
                if not await user_exists_in_room(db, username, room_id):
                    payload = {"successful": False, "description": "Inviter not in room"}

                    # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
                    await sio.emit("add_to_room_response", payload, to=sid)
                    raise Exception("Inviter is not in room")

            # The user being invited can not be in the room they are being invited to
            if await user_exists_in_room(db, new_user, room_id):
                payload = {"successful": False, "description": f"User '{new_user}' is already in the room"}
                # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
                await sio.emit("add_to_room_response", payload, to=sid)
                raise Exception("Invited user already exists in room")

            # Add user to the database
            await add_user_to_chat_room(db, new_user, room_id)

            # If the user is currently online, notify them immediately
            if new_user in user_sockets_mapping:
                new_user_sid = user_sockets_mapping[new_user]

                # Make the user receive notifications for the room
                await sio.enter_room(new_user_sid, room_id)

                # Fetch the new list of rooms that the invited user is in
                rooms = await get_user_rooms(db=db, username=new_user)
                payload = {
                    "successful": True,
                    "description": "",
                    "payload": rooms
                }

                # Notify the invited user
                # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
                await sio.emit("return_user_rooms", payload, to=new_user_sid)

        # Notify the inviter that the invitation was succesful
        payload = {"successful": True, "description": "Room joined succesfully"}
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("add_to_room_response", payload, to=sid)

    except ValueError:
        payload = {"successful": False, "description": "Invalid room ID"}
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("add_to_room_response", payload, to=sid)

    except KeyError:
        payload = {"successful": False, "description": "No username found in session"}
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("add_to_room_response", payload, to=sid)

    except Exception as e:
        print(f"Exception occurred while joining a room: {e}")
        payload = {"successful": False, "description": "Error occurred while joining a room"}
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("add_to_room_response", payload, to=sid)


@sio.on("get_user_rooms")
async def get_user_chats(sid, _=None):
    print("get_user_rooms sid:", sid)
    async with sio.session(sid) as session:
        # TODO: Error if username doesn't exist
        username = session["username"]
        rooms = await get_user_rooms(db=db, username=username)
        payload = {
            "successful": True,
            "description": "",
            "payload": rooms
        }
        print("ROOMS:", rooms)
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("return_user_rooms", payload, to=sid)


@sio.on("fetch_room_messages")
async def fetch_room_messages(sid, room_id):
    print("fetch_room_messages room_id", room_id)
    room_id = int(room_id)

    async with sio.session(sid) as session:
        # TODO: Error if username doesn't exist
        username = session["username"]
        print("Session username:", username)
        if not await user_exists_in_room(db, username, room_id):
            print("User not in room")
            payload = {"successful": False, "description": "User is not in the room"}
            # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
            await sio.emit("fetch_room_messages_response", payload, to=sid)
            raise Exception("No permission to join the room")

        messages = await get_messages(db, room_id)
        payload = {
            "successful": True,
            "description": "",
            "messages": messages
        }

        print(messages)
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("fetch_room_messages_response", payload, to=sid)


@sio.on("send_msg")
async def send_message(sid, message, room_id):
    try:
        print(f"send_message called {message} to room id: {room_id}")
        room_id = int(room_id)

        # Get the user name from the session
        session = await sio.get_session(sid)
        # TODO: Error if username doesn't exist
        username = session["username"]

        if not await user_exists_in_room(db, username, room_id):
            payload = {
                "successful": False,
                "description": "User is not in the room",
                "data": None
            }
            # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
            await sio.emit("receive_msg", data=payload, to=sid)
            raise Exception("no permission to send messages to the room")
        # Save the message
        await save_message(db, username, room_id, message)
        # print("Message has been saved")

        # Prepare data to emit
        data = {
            "sender": username,
            "content": message,
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
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("receive_msg", data=payload, room=room_id)
        # print("Sent payload")

    except ValueError as ve:
        print(f"ValueError: {ve}")

    except JWTError as e:
        print(f"JWT ERROR: {e}")

    except Exception as e:
        print(f"Exception occurred while sending message: {e}")

# keep track of document structure and its order.

# counter = 0

# def create_unique_position_between(a: str, b: str, username: str) -> str:
#     global counter
#     # A globally unique new string, in the form of a causal dot.
#     unique_str = f"{username}{counter}"
#     counter += 1

#     if a is not None and b is not None:
#         if not b.startswith(a):
#             # a is not a prefix of b.
#             return f"{a}{unique_str}R"
#         else:
#             # a is a strict prefix of b.
#             b_with_l = f"{b[:-1]}L"
#             return f"{b_with_l}{unique_str}R"
#     else:
#         # Edge cases.
#         if b is None:
#             # Treat a (possibly undefined) as not a prefix of b.
#             return f"{a or ''}{unique_str}R"
#         else:
#             # Treat a (undefined) as a strict prefix of b.
#             b_with_l = f"{b[:-1]}L"
#             return f"{b_with_l}{unique_str}R"


# def serialize(obj):
#     if isinstance(obj, DocumentItem):
#         return obj.to_json
#     else:
#         raise TypeError("Object of type MyClass is not JSON serializable")

files : Dict[int, List[DocumentItem]] = {}

@sio.on("upload_document")
async def upload_document(sid, room_id, json_data, filename):
    try:
        print(f"upload_document called {json_data} to room id: {room_id}")
        room_id = int(room_id)

        # Get the user name from the session
        session = await sio.get_session(sid)
        
        # TODO: Error if username doesn't exist
        username = session["username"]

        check_user_exists_in_room(sid, "upload_document_response", username, room_id)

        file_id = await save_file(db, room_id, filename)
        files[file_id] = []

        data = json.loads(json_data)
        for item in data:
            print(f'value: {item["value"]}, position: {item["position"]}')
            document_item = DocumentItem(value=item["value"], position=item["position"])
            files[file_id].append(document_item)

        data = [item.__dict__ for item in files[file_id]]

        response = {
            "successful": True,
            "data": data,
            "document_id": file_id
        }
        await sio.emit("upload_file_response", room=room_id, data=response)

    except Exception as e:
        print(f'Exception occured while uploading document: {e}')


@sio.on("join_file_edit")
async def join_file_edit(sid, file_id):
    try:
        print(f"join_document_edit called for document id: {file_id}")
        file_id = int(file_id)

        # Get the user name from the session
        session = await sio.get_session(sid)

        # TODO: Error if username doesn't exist
        username = session["username"]

        file = await get_file(db, file_id)
        room_id = file['room_id']

        check_user_exists_in_room(sid, "join_file_edit_response", username, room_id)

        await sio.enter_room(sid=sid, room=file_id)
        file_id = file['id']
        response = {
            "successful": True,
            "Description": f"Joined the document editing successfully to id: {file_id}",
            "data": files[file_id]
        }
        await sio.emit("join_file_edit_response", room=sid, data=response)
    except Exception as e:
        print(f'Exception occured while joining the room for document editing')


@sio.on("update_file")
async def update_document(sid, file_id, operation_type, char, position):
    try:
        print(f'update_document has been called')
        file_id = int(file_id)

        # Get the user name from the session
        session = await sio.get_session(sid)

        # TODO: Error if username doesn't exist
        username = session["username"]

        file = await get_file(db, file_id)
        room_id = file['room_id']
        check_user_exists_in_room(sid, "update_file_response", username, room_id)
        
        data = {
            "operation_type": operation_type,
            "file_id": file_id,
            "char": char,
            "position": position
        }

        response = {
            "successful": True,
            "description": "",
            "data": data
        }
        await sio.emit("update_document_response", room=file_id, data=response)

    except Exception as e:
        print(f"error while updateing document: {e}")

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
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("receive_throughput", data=binary_payload, to=sid)
        packets_sent += 1
        end_time = datetime.now()

    throughput_kbps = (packets_sent * 1024) / (end_time - start_time).total_seconds()

    print("GOT THROUGHPUT:", throughput_kbps)

    # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
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
    async with sio.session(sid) as session:
        # TODO: Error if username doesn't exist
        username = session["username"]
        user_sockets_mapping.pop(username)

        print(f"Removing user {username} from active users")
        await set_user_activity(db, username, False)

        user_update_payload = {
                "username": username,
                "active": False
            }

        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("user_activities_update", user_update_payload, skip_sid=sid)


@sio.on("ping_ack")
async def ping_ack(sid, time_string):
    # print("Received ping_ack with time:", time_string)
    async with sio.session(sid) as session:
        # TODO: Error if username doesn't exist
        username = session["username"]
        current_time = datetime.now()
        ack_time = datetime.fromisoformat(time_string)

        # Returns the time difference in milliseconds
        time_difference = int((current_time - ack_time).total_seconds() * 1000)

        # print("Emitting time difference")

        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("ping_result", data=(time_difference, username))


async def scheduled_ping():
    # print("IN SCHEDULED TASK!!")
    while True:
        # print("Waiting for 10 sec and sending ping")
        await sio.sleep(10)
        payload = str(datetime.now())
        print("Emitting payload:", payload)
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit("ping", payload)


async def check_user_exists_in_room(sid, event_to_emit, username, room_id):
    if not await user_exists_in_room(db, username, room_id):
        payload = {
            "successful": False,
            "description": "User is not in the room",
            "data": None
        }
        # TODO: await sio.emit("event", data=(succesful, description, rooms), to=sid)
        await sio.emit(event_to_emit, data=payload, to=sid)
        raise Exception("no permission to send messages to the room")       
            

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
