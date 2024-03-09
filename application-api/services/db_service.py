from databases import Database
from typing import List


async def insert_room(db: Database, room_name: str) -> int:
    query = "INSERT INTO rooms (name) VALUES (:name) RETURNING id"
    values = {"name": room_name}
    room_id = await db.execute(query=query, values=values)
    return room_id


async def insert_user_room_mapping(db: Database, user_name: str, room_id: int) -> None:
    query = "INSERT INTO user_room_mappings(user_name, room_id) VALUES (:user_name, :room_id)"
    values = {"user_name": user_name, "room_id": room_id}
    await db.execute(query=query, values=values)


async def check_user_exists(db: Database, username: str) -> bool:
    query = "SELECT * FROM users WHERE username = :username"
    values = {"username": username}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def get_user(db: Database, username, password):
    return await db.fetch_one(
        query="SELECT * FROM users WHERE username = :username AND password = :password",
        values={"username": username, "password": password},
    )


async def user_exists_in_room(db: Database, username: str, room_id: int) -> bool:
    query = "SELECT * FROM user_room_mappings WHERE user_name = :username AND room_id = :room_id"
    values = {"username": username, "room_id": room_id}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def save_message(db: Database, sender: str, room_id: int, content: str):
    query = "INSERT INTO messages (sender, room_id, content) VALUES (:sender, :room_id, :content)"
    values = {"sender": sender, "room_id": room_id, "content": content}
    await db.execute(query=query, values=values)


async def get_messages(db: Database, room_id: int, offset: int = 0):
    query = "SELECT sender as sender, content, timestamp FROM messages WHERE room_id = :room_id ORDER BY timestamp DESC LIMIT 50 OFFSET :offset"  # noqa
    values = {"room_id": room_id, "offset": offset}

    rows = await db.fetch_all(query=query, values=values)
    # Return the list of messages
    rows = [dict(row) for row in rows]
    for row in rows:
        row["timestamp"] = row["timestamp"].isoformat()

    return rows


# async def get_friendly_name_for_user(db: Database, username):
#     query = "SELECT friendly_name FROM users WHERE name = :username"
#     values = {"username": username}
#     result = await db.fetch_one(query=query, values=values)
#     return result["friendly_name"] if result else None


async def get_user_rooms(db: Database, username):
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
    query = "SELECT user_name, room_id FROM user_room_mappings" # noqa

    result = await db.fetch_all(query=query)

    mappings = [
        {
            "room_id": record["room_id"],
            "user_name": record["user_name"]
         }
        for record in result]

    return mappings
