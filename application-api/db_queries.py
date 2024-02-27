
from databases import Database
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a connection to the PostgreSQL database
database = Database(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to db on startup
    await database.connect()
    yield
    # Disconnect from db on shutdown
    await database.disconnect()

async def insert_room(room_name: str) -> int:
    query = "INSERT INTO rooms (name) VALUES (:name) RETURNING id"
    values = {"name": room_name}
    room_id = await database.execute(query=query, values=values)
    return room_id

async def insert_user_room_mapping(user_name: str, room_id: int) -> None:
    query = "INSERT INTO user_room_mappings(user_name, room_id) VALUES (:user_name, :room_id)"
    values = {"user_name": user_name, "room_id": room_id}
    await database.execute(query=query, values=values)

async def check_user_exists(username: str) -> bool:
    query="SELECT * FROM users WHERE name = :username"
    values = {"username": username}
    response = await database.execute(query=query, values=values)
    return bool(response)

async def get_user(username, password):
    return await database.fetch_one(
        query="SELECT * FROM users WHERE name = :username AND password = :password",
        values={"username": username, "password": password},
    )

async def user_exists_in_room(username: str, room_id: int) -> bool:
    query = "SELECT * FROM user_room_mappings WHERE user_name = :username AND room_id = :room_id"
    values = {"username": username, "room_id": room_id}
    response = await database.execute(query=query, values=values)
    return bool(response)

async def save_message(sender_name: str, room_id: int, message: str):
    query = "INSERT INTO messages (sender_name, room_id, message) VALUES (:sender_name, :room_id, :message)"
    values = {"sender_name": sender_name, "room_id": room_id, "message": message}
    await database.execute(query=query, values=values)

async def get_messages(room_id: int, offset: int = 0): 
    query = "SELECT sender_name as sender, message, sent FROM messages WHERE room_id = :room_id ORDER BY sent DESC LIMIT 50 OFFSET :offset"
    values = {"room_id": room_id, "offset": offset}

    rows = await database.fetch_all(query=query, values=values)
    # Return the list of messages
    rows = [dict(row) for row in rows]
    for row in rows:
        row['sent'] = row['sent'].isoformat()

    return rows