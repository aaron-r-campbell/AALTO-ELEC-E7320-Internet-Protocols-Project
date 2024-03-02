from databases import Database


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
    query = "SELECT * FROM users WHERE name = :username"
    values = {"username": username}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def get_user(db: Database, username, password):
    return await db.fetch_one(
        query="SELECT * FROM users WHERE name = :username AND password = :password",
        values={"username": username, "password": password},
    )


async def user_exists_in_room(db: Database, username: str, room_id: int) -> bool:
    query = "SELECT * FROM user_room_mappings WHERE user_name = :username AND room_id = :room_id"
    values = {"username": username, "room_id": room_id}
    response = await db.execute(query=query, values=values)
    return bool(response)


async def save_message(db: Database, sender_name: str, room_id: int, message: str):
    query = "INSERT INTO messages (sender_name, room_id, message) VALUES (:sender_name, :room_id, :message)"
    values = {"sender_name": sender_name, "room_id": room_id, "message": message}
    await db.execute(query=query, values=values)


async def get_messages(db: Database, room_id: int, offset: int = 0):
    query = "SELECT sender_name as sender, message, sent FROM messages WHERE room_id = :room_id ORDER BY sent DESC LIMIT 50 OFFSET :offset"
    values = {"room_id": room_id, "offset": offset}

    rows = await db.fetch_all(query=query, values=values)
    # Return the list of messages
    rows = [dict(row) for row in rows]
    for row in rows:
        row["sent"] = row["sent"].isoformat()

    return rows


async def get_friendly_name_for_user(db: Database, username):
    query = "SELECT friendly_name FROM users WHERE name = :username"
    values = {"username": username}
    result = await db.fetch_one(query=query, values=values)
    return result["friendly_name"] if result else None
