import asyncio
from bleak import BleakClient, BleakScanner
import socket

DEVICE_NAME = "Tolkyn"
CHAR_UUID = "2A57"

UDP_ID = "127.0.0.1"
UDP_PORT = 6000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def handle_notification(sender, data):
    try:
        text = data.decode('utf-8').strip()
        sock.sendto(text.encode('utf-8'), (UDP_ID, UDP_PORT))
    except Exception as e:
        print(f"Error handling notification: {e}")

async def main():
    devices = await BleakScanner.discover()
    
    target = None
    for d in devices:
        if d.name == DEVICE_NAME:
            target = d
            break

    if target is None:
        print(f"Device {DEVICE_NAME} not found.")
        return
    
    async with BleakClient(target.address) as client:
        if not client.is_connected:
            print("Failed to connect to the device.")
            return
        
        await client.start_notify(CHAR_UUID, handle_notification)

        while True:
            await asyncio.sleep(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    sock.close()

