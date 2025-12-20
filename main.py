import socket, json

s = socket.socket()
s.bind(("localhost", 5005))
s.listen(1)

print("Waiting for Processing...")
conn, _ = s.accept()
print("Processing connected")

conn_file = conn.makefile("rwb")  # read/write buffered

while True:
    line = conn_file.readline()
    if not line:
        break

    state = json.loads(line.decode())
    print("From Processing:", state)

    # AI logic here
    response = {
        "angleBoostX": state.get("angleX", 0) * 0.5
    }

    #conn_file.write((json.dumps(response) + "\n").encode())
    #conn_file.flush()
