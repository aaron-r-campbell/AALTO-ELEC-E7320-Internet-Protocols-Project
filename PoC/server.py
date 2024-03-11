from fastapi import FastAPI, Depends, HTTPException, Request, Response
import socketio

app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

@sio.on("ping")
async def ping(sid, data):
  print("Got ping:", sid, data)


if __name__ == "__main__":
    import uvicorn
    print("Starting server!")

    uvicorn.run(app, host="127.0.0.1", port=7777)
