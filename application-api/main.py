from fastapi import FastAPI  # noqa
from socketio import AsyncServer, ASGIApp

from utils.db_util import lifespan
from services import fastapi_service, socketio_service

# Initialize FastAPI application
app = FastAPI(lifespan=lifespan)

# Initialize Socket.IO server
sio = AsyncServer(cors_allowed_origins="*", async_mode="asgi")
sio.background_task_started = False

# Wrap with ASGI application
socket_app = ASGIApp(sio)
app.mount("/", socket_app)

# Initialize FastAPI service
fastapi_service.setup(app)

# Initialize Socket.IO service
socketio_service.setup(sio)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7777)
