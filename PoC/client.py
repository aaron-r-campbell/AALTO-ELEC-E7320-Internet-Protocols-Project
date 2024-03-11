import socketio
import asyncio

sio = socketio.AsyncClient()


@sio.event
def connect():
    print("Connected to server")
    asyncio.create_task(emit_pings())


async def emit_pings():
    for i in range(100000):
        print("Sending ping", i)
        await sio.emit("ping", data=i)

if __name__ == "__main__":
    # This code will only be executed when the script is run directly
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sio.connect("http://127.0.0.1:7777/"))

    print("Connection successful")
