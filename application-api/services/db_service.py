from databases import Database
from typing import List, Dict, Any


# Users


async def get_all_users(db: Database) -> List[Dict[str, Any]]:
    query = "SELECT username FROM users;"
    response = await db.fetch_all(query=query)
    return [dict(user) for user in response]


async def user_exists(db: Database, username: str) -> bool:
    query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = :username);"
    values = {"username": username}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def get_user(db: Database, username: str, password: str) -> Dict:
    query = "SELECT * FROM users WHERE username = :username AND password = :password;"
    values = {"username": username, "password": password}
    response = await db.fetch_one(query=query, values=values)
    return dict(response)


# Rooms


async def create_room(db: Database, chatroom_name: str, creator_username: str) -> int:
    async with db.transaction():
        if not await user_exists(db=db, username=creator_username):
            raise Exception(f"User {creator_username} does not exist.")
        query = "INSERT INTO rooms (name) VALUES (:name) RETURNING id;"
        values = {"name": chatroom_name}
        room_id = await db.execute(query=query, values=values)
        return room_id


async def room_exists(db: Database, room_id: str) -> bool:
    query = "SELECT EXISTS(SELECT 1 FROM rooms WHERE id = :room_id);"
    values = {"room_id": room_id}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def room_exists_by_name(db: Database, room_name: str) -> bool:
    query = "SELECT EXISTS(SELECT 1 FROM rooms WHERE name = :room_name);"
    values = {"room_name": room_name}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def get_room_name(db: Database, room_id: int) -> str:
    async with db.transaction():
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        query = "SELECT name FROM rooms WHERE id = :room_id;"
        values = {"room_id": room_id}
        response = await db.fetch_one(query=query, values=values)
        return response


async def delete_room(db: Database, room_id: int):
    async with db.transaction():
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        messages_query = "DELETE FROM messages WHERE room_id = :room_id;"
        messages_values = {"room_id": room_id}
        await db.execute(query=messages_query, values=messages_values)

        query_files = "DELETE FROM files WHERE room_id = :room_id"
        values_files = {"room_id": room_id}
        await db.execute(query=query_files, values=values_files)

        mappings_query = "DELETE FROM user_room_mappings WHERE room_id = :room_id;"
        mappings_values = {"room_id": room_id}
        await db.execute(query=mappings_query, values=mappings_values)

        rooms_query = "DELETE FROM rooms WHERE id = :room_id;"
        rooms_values = {"room_id": room_id}
        await db.execute(query=rooms_query, values=rooms_values)


# Mappings


async def get_all_user_room_mappings(db: Database) -> List[int]:
    query = "SELECT user_name, room_id FROM user_room_mappings;"
    response = await db.fetch_all(query=query)
    return [dict(user_room_mapping) for user_room_mapping in response]


async def add_user_to_room(db: Database, username: str, room_id: int):
    async with db.transaction():
        if not await user_exists(db=db, username=username):
            raise Exception(f"User {username} does not exist.")
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        query = "INSERT INTO user_room_mappings (user_name, room_id) VALUES (:username, :room_id);"
        values = {"username": username, "room_id": room_id}
        await db.execute(query=query, values=values)


async def user_exists_in_room(db: Database, username: str, room_id: int) -> bool:
    async with db.transaction():
        if not await user_exists(db=db, username=username):
            raise Exception(f"User {username} does not exist.")
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        query = "SELECT * FROM user_room_mappings WHERE user_name = :username AND room_id = :room_id;"
        values = {"username": username, "room_id": room_id}
        response = await db.fetch_one(query=query, values=values)
        return bool(response)


async def get_users_not_in_room_by_id(db: Database, room_id: int) -> List[str]:
    async with db.transaction():
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        query = """
            SELECT username
            FROM users
            WHERE NOT EXISTS (
                SELECT 1
                FROM user_room_mappings
                WHERE user_name = users.username
                AND room_id = :room_id
            );
            """
        values = {"room_id": room_id}
        response = await db.fetch_all(query=query, values=values)
        return [dict(user) for user in response]


async def get_rooms_by_user(db: Database, username: str) -> List[Dict]:
    async with db.transaction():
        if not await user_exists(db=db, username=username):
            raise Exception(f"User {username} does not exist.")
        query = "SELECT rooms.id AS room_id, rooms.name AS room_name FROM user_room_mappings, rooms WHERE rooms.id = user_room_mappings.room_id AND user_name = :username;"  # noqa
        values = {"username": username}
        response = await db.fetch_all(query=query, values=values)
        return [dict(room) for room in response]


# Messages


async def create_message(db: Database, sender: str, room_id: int, content: str) -> int:
    async with db.transaction():
        if not await user_exists(db=db, username=sender):
            raise Exception(f"User {sender} does not exist.")
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        query = "INSERT INTO messages (sender, room_id, content) VALUES (:sender, :room_id, :content) RETURNING id;"
        values = {"sender": sender, "room_id": room_id, "content": content}
        message_id = await db.execute(query=query, values=values)
        return message_id


async def get_messages_by_room(
    db: Database, room_id: int, offset: int = 0
) -> List[Dict]:
    async with db.transaction():
        if not await room_exists(db=db, room_id=room_id):
            raise Exception(f"Room with id {room_id} does not exist.")
        query = "SELECT sender as sender, content, timestamp FROM messages WHERE room_id = :room_id ORDER BY timestamp ASC LIMIT 50 OFFSET :offset"  # noqa
        values = {"room_id": room_id, "offset": offset}
        response = await db.fetch_all(query=query, values=values)
        return [{**row, "timestamp": row["timestamp"].isoformat()} for row in response]


# Files


async def create_file(db: Database, room_id, filename) -> int:
    query = (
        "INSERT INTO files (room_id, name) VALUES (:room_id, :filename) RETURNING id;"
    )
    values = {"room_id": room_id, "filename": filename}
    file_id = await db.execute(query=query, values=values)
    return file_id

async def get_files(db: Database, room_id: int):
    # TODO: Check that room_id exists
    # TODO: async with db.transaction():
    query = "SELECT name, id FROM files WHERE room_id = :room_id ORDER BY name DESC"  # noqa
    values = {"room_id": room_id}

    response = await db.fetch_all(query=query, values=values)
    return [dict(file) for file in response]


async def file_exists(db: Database, file_id: str) -> bool:
    query = "SELECT EXISTS(SELECT 1 FROM files WHERE id = :file_id);"
    values = {"file_id": file_id}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def update_file(db: Database, file_id: str, content: str):
    query = "UPDATE files (content) VALUES (:content) WHERE id = :file_id;"
    values = {"content": content, "file_id": file_id}
    await db.execute(query=query, values=values)


async def get_file(db: Database, file_id: str) -> Dict:
    async with db.transaction():
        if not await file_exists(db=db, file_id=file_id):
            raise Exception(f"File with id {file_id} does not exist.")
        query = "SELECT * FROM files WHERE id = :file_id;"
        values = {"file_id": file_id}
        response = await db.fetch_one(query=query, values=values)
        return dict(response)
