from fastapi import FastAPI  # noqa
from fastapi.middleware.cors import CORSMiddleware

from utils.db_util import lifespan
from services import fastapi_service, socketio_service
# from typing import Dict, List
# from models.data import DocumentItem

# Initialize FastAPI application
app = FastAPI(lifespan=lifespan)

# Add FastAPI routes
app.include_router(fastapi_service.router)

origins = ["http://localhost:7800", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", socketio_service.socket_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
