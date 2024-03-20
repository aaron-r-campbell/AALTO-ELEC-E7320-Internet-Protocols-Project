# Used in conjunction with the main program. 
import socketio
import asyncio
from multiprocess import Process, Queue  # noqa
import requests
import time
from datetime import datetime

sio = socketio.AsyncClient(ssl_verify=False)  # logger=True, engineio_logger=True
global_token = None
ping_start_time = None
ping_end_time = None

@sio.on("authenticate_ack")
def auth_ack(sid, payload):
    print("authenticate_ack got payload", payload, "with sid", sid)


@sio.event
def connect():
    print("Connected to server")
    # asyncio.create_task(emit_pings())
    # asyncio.create_task(emit_pings())
    asyncio.create_task(sio.emit("authenticate", data=global_token))
    print("emitting authenticate with token:", global_token)


@sio.on("authenticate_ack")
async def auth_ack(sid, payload):
    print("Got auth_ack with payload:", payload)


# async def emit_pings():
#     print("In emit pings")
#     for i in range(5):
#         print(i)
#         time.sleep(1)
#         await sio.emit("ping_ack", data=str(datetime.now()))
#         ping_start_time = datetime.now()


@sio.on("ping_result")
def ping_res(sid, time_dif, username):
    print("Got time diff", time_dif, "from", username)
    ping_end_time = datetime.now()
    delay = (ping_end_time - ping_start_time).total_seconds()

    print("This is the delay:", delay)


@sio.event
def disconnect():
    print("Disconnecting from the server")


async def run_sio_events(token):
    print("In run_sio_events, this is the token:", token)
    await sio.connect("https://localhost:7800/")


# async def emit_pings():
#     for i in range(100000):
#         print("Sending ping", i)
#         await sio.emit("ping", data=i)


def send_throughput_test(headers, num_kb, idx):
    # print(headers, num_kb)
    url_download = f"https://localhost:7800/api/throughput_download?size_kb={num_kb}"
    response_download = requests.get(url_download, headers=headers, verify=False)
    print(idx, response_download)

if __name__ == "__main__":
    # This code will only be executed when the script is run directly

    requests.packages.urllib3.disable_warnings()

    url_token = "https://localhost:7800/api/token"
    payload = {"username": "user1", "password": "pass1"}
    headers = {"Content-Type": "application/json"}

    response_token = requests.post(url_token, json=payload, headers=headers, verify=False)
    response_json = response_token.json()
    print(response_json)

    bearer_token = f"{response_json['token_type']} {response_json['token']}"
    global_token = response_json['token']

    test_headers = {"Authorization": bearer_token}

    # print(bearer_token)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sio_events(response_json['token']))

    time.sleep(10)

    # loop.run_until_complete(sio.disconnect())

    # time.sleep(5)

    exit()

    processes = []

    for idx in range(10):
        processes.append(Process(target=send_throughput_test, args=(test_headers, 10000, idx)))

    for proc in processes:
        proc.start()
    
    for proc in processes:
        proc.join()

    # q = Queue()
    # def f(q):
    #     q.put('hello world')
    # p = Process(target=f, args=[q])
    
    # p.start()
    # print (q.get())
    # p.join()

    # print("Connection successful")
