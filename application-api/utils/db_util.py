from contextlib import asynccontextmanager
from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI
import os

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")


# Create a connection to the PostgreSQL database
db = Database(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to db on startup
    await db.connect()
    yield
    # Disconnect from db on shutdown
    await db.disconnect()