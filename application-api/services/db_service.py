from databases import Database
from typing import List, Dict, Any


# async def insert_room(db: Database, room_name: str) -> int:
#     query = "INSERT INTO rooms (name) VALUES (:name) RETURNING id"
#     values = {"name": room_name}
#     room_id = await db.execute(query=query, values=values)
#     return room_id


# async def insert_user_room_mapping(db: Database, user_name: str, room_id: int) -> None:
#     query = "INSERT INTO user_room_mappings(user_name, room_id) VALUES (:user_name, :room_id)"
#     values = {"user_name": user_name, "room_id": room_id}
#     await db.execute(query=query, values=values)


async def check_user_exists(db: Database, username: str) -> bool:
    query = "SELECT * FROM users WHERE username = :username"
    values = {"username": username}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def get_user(db: Database, username, password):
    # TODO: Add error handling for when user is not in database
    return await db.fetch_one(
        query="SELECT * FROM users WHERE username = :username AND password = :password",
        values={"username": username, "password": password},
    )


async def user_exists_in_room(db: Database, username: str, room_id: int) -> bool:
    # TODO: Check that user exists first with check_user_exists
    # TODO: async with db.transaction():
    query = "SELECT * FROM user_room_mappings WHERE user_name = :username AND room_id = :room_id"
    values = {"username": username, "room_id": room_id}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def save_message(db: Database, sender: str, room_id: int, content: str):
    # OPTIONAL TODO: Return message ID
    # OPTIONAL TODO: Check that room_id and sender exist
    query = "INSERT INTO messages (sender, room_id, content) VALUES (:sender, :room_id, :content)"
    values = {"sender": sender, "room_id": room_id, "content": content}
    await db.execute(query=query, values=values)


async def get_messages(db: Database, room_id: int, offset: int = 0):
    # TODO: Check that room_id exists
    # TODO: async with db.transaction():
    query = "SELECT sender as sender, content, timestamp FROM messages WHERE room_id = :room_id ORDER BY timestamp DESC LIMIT 50 OFFSET :offset"  # noqa
    values = {"room_id": room_id, "offset": offset}

    rows = await db.fetch_all(query=query, values=values)
    # Return the list of messages
    rows = [dict(row) for row in rows]
    for row in rows:
        row["timestamp"] = row["timestamp"].isoformat()

    return rows


async def get_user_rooms(db: Database, username: str):
    # TODO: Check that username exists
    # TODO: async with db.transaction():
    query = "SELECT rooms.id AS room_id, rooms.name AS room_name FROM user_room_mappings, rooms WHERE rooms.id = user_room_mappings.room_id AND user_name = :username" # noqa
    values = {"username": username}
    result = await db.fetch_all(query=query, values=values)

    room_ids = [
        {
            "room_id": record["room_id"],
            "room_name": record["room_name"]
         }
        for record in result]

    return room_ids


async def get_all_user_room_mappings(db: Database) -> List[int]:
    query = "SELECT user_name, room_id FROM user_room_mappings"

    result = await db.fetch_all(query=query)

    mappings = [
        {
            "room_id": record["room_id"],
            "user_name": record["user_name"]
         }
        for record in result]

    return mappings


async def get_all_users(db: Database) -> List[Dict[str, Any]]:
    query = "SELECT username, active, last_seen FROM users"

    result = await db.fetch_all(query=query)

    users = [
        {
            "username": record["username"],
            "active": record["active"]
         }
        for record in result]

    return users


async def set_user_activity(db: Database, username: str, active: bool):
    # TODO: Check that username exists
    # TODO: async with db.transaction():
    query = "UPDATE users SET active = :active WHERE username = :username"

    values = {
        "username": username,
        "active": active
    }

    await db.execute(query=query, values=values)


async def create_chat_room(db: Database, chatroom_name: str, creator_username: str):
    # Both creates the room and inserts the user into the room
    async with db.transaction():
        # TODO: Check that chatroom_name exists and username exists
        query = "INSERT INTO rooms (name) VALUES (:name)"
        values = {"name": chatroom_name}
        await db.execute(query=query, values=values)

        query = "SELECT lastval() AS last_insert_id"
        last_insert_id = await db.fetch_val(query=query)

        print("THIS IS THE INSERTED VALUE", last_insert_id)

        await add_user_to_chat_room(db, creator_username, last_insert_id)

        return last_insert_id


async def add_user_to_chat_room(db: Database, username: str, room_id: int):
    # TODO: Check that username exists, Check that room_id exists
    # TODO: async with db.transaction():
    query = "INSERT INTO user_room_mappings (user_name, room_id) VALUES (:username, :room_id)"
    values = {
        "username": username,
        "room_id": room_id
        }
    await db.execute(query=query, values=values)


async def check_roomid_exists(db: Database, roomid: str):
    query = "SELECT EXISTS(SELECT 1 FROM rooms WHERE id = :roomid)"
    values = {"roomid": roomid}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def check_roomname_exists(db: Database, room_name: str):
    query = "SELECT EXISTS(SELECT 1 FROM rooms WHERE name = :roomname)"
    values = {"roomname": room_name}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def get_usernames_not_in_room(db: Database, room_id: int):
    # TODO: Check that room_id exists
    # TODO: async with db.transaction():
    query = """
        SELECT username
        FROM users
        WHERE NOT EXISTS (
            SELECT 1
            FROM user_room_mappings
            WHERE user_room_mappings.user_name = users.username
            AND user_room_mappings.room_id = :room_id
        );
        """

    values = {
        "room_id": room_id
    }
    result = await db.fetch_all(query=query, values=values)

    users = [
        {
            "username": record["username"]
         }
        for record in result]

    return users


async def get_roomname_by_id(db: Database, room_id: int):
    # TODO: Check that room_id exists
    query = "SELECT name FROM rooms WHERE id = :room_id"
    values = {"room_id": room_id}
    result = await db.fetch_one(query=query, values=values)
    if result:
        return result["name"]
    else:
        return None


async def delete_room_by_id(db: Database, room_id: int):
    # TODO: Check that room_id exists
    async with db.transaction():
        query_messages = "DELETE FROM messages WHERE room_id = :room_id"
        values_messages = {"room_id": room_id}
        await db.execute(query=query_messages, values=values_messages)

        query_mappings = "DELETE FROM user_room_mappings WHERE room_id = :room_id"
        values_mappings = {"room_id": room_id}
        await db.execute(query=query_mappings, values=values_mappings)

        query_rooms = "DELETE FROM rooms WHERE id = :room_id"
        values_rooms = {"room_id": room_id}
        await db.execute(query=query_rooms, values=values_rooms)


async def get_roomname_by_id(db: Database, room_id: int):
    # TODO: Check that room_id exists
    query = "SELECT name FROM rooms WHERE id = :room_id"
    values = {"room_id": room_id}
    result = await db.fetch_one(query=query, values=values)
    if result:
        return result["name"]
    else:
        return None


async def delete_room_by_id(db: Database, room_id: int):
    # TODO: Check that room_id exists
    async with db.transaction():
        query_messages = "DELETE FROM messages WHERE room_id = :room_id"
        values_messages = {"room_id": room_id}
        await db.execute(query=query_messages, values=values_messages)

        query_files = "DELETE FROM files WHERE room_id = :room_id"
        values_files = {"room_id": room_id}
        await db.execute(query=query_files, values=values_files)

        query_mappings = "DELETE FROM user_room_mappings WHERE room_id = :room_id"
        values_mappings = {"room_id": room_id}
        await db.execute(query=query_mappings, values=values_mappings)

        query_rooms = "DELETE FROM rooms WHERE id = :room_id"
        values_rooms = {"room_id": room_id}
        await db.execute(query=query_rooms, values=values_rooms)

async def save_file(db: Database, room_id, filename):
    query = "INSERT INTO files (room_id, name) VALUES (:room_id, :filename) RETURNING id;"
    values = {"room_id": room_id, "filename": filename}
    file_id = await db.execute(query=query, values=values)
    return file_id

async def get_file(db: Database, file_id): 
    query = "SELECT * FROM files WHERE id = :file_id;"
    values = {"file_id": file_id}
    record = await db.fetch_one(query=query, values=values)
    if record is None:
        raise Exception(f"File does not exist for the given file id: {file_id}")
    return record