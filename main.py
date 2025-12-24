import socket
import json
import time
#from aiengine import SpoonRotationController

HOST = "localhost"
PORT = 5005
AI_INTERVAL = 1.5  # seconds

print("Starting Tolqyn AI server...")

#controller = SpoonRotationController()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(1)

print("Waiting for Processing...")
conn, addr = sock.accept()
print("Processing connected:", addr)

conn_file = conn.makefile("rwb")

last_ai_time = 0.0
last_response = {}

ax = "" 
ay = ""
az = ""

while True:
    line = conn_file.readline()
    if not line:
        print("Processing disconnected")
        break

    try:
        msg = json.loads(line.decode())
        ax = msg.get("angleX", 0.0)
        ay = msg.get("angleY", 0.0)
        az = msg.get("angleZ", 0.0)
        print("[From Processing]", msg, flush=True)
    except json.JSONDecodeError:
        print("JSON error")

    now = time.time()

    # ---- Throttled AI reasoning ----
    if now - last_ai_time >= AI_INTERVAL:
        #ai = controller.get_rotation_gains(ax, ay, az)
        #if ai:
            # last_response = {
            #     "mode": ai.get("mode", "calm"),
            #     "rotationGainX": ai.get("rotationGainX", 0.3),
            #     "rotationGainY": ai.get("rotationGainY", 0.3),
            #     "rotationGainZ": ai.get("rotationGainZ", 0.3)
            # }
        last_response = {
            "angleX" : ax,
            "angleY" : ay,
            "angleZ" : az
        }
        last_ai_time = now
        print("[From Python]", last_response)

    # ---- Always send last known safe values ----
    conn_file.write((json.dumps(last_response) + "\n").encode())
    conn_file.flush()
