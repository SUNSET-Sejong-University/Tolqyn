import asyncio
from bleak import BleakClient, BleakScanner
import socket

DEVICE_NAME = "Tolkyn"
GYRO_CHAR_UUID = "2A57"
CMD_CHAR_UUID = "2A58"

UDP_HOST = "127.0.0.1"
UDP_GYRO_PORT = 6000
UDP_CMD_PORT = 6001

sock_gyro = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_cmd.bind((UDP_HOST, UDP_CMD_PORT))
sock_cmd.setblocking(False)

def handle_notification(sender, data):
    try:
        text = data.decode('utf-8').strip()
        sock_gyro.sendto(text.encode('utf-8'), (UDP_HOST, UDP_GYRO_PORT))
    except Exception as e:
        print(f"Error handling notification: {e}")

async def find_device():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == DEVICE_NAME:
            return d
    return None

async def udp_command_task(client):
    while True:
        try:
            data, _ = sock_cmd.recvfrom(1024)
            command = data.decode('utf-8').strip()
            if command:
                await client.write_gatt_char(CMD_CHAR_UUID, command.encode('utf-8'))
        except BlockingIOError:
            await asyncio.sleep(0.1)


async def main():
    device = await find_device()
    if not device:
        return

    async with BleakClient(device.address) as client:
        if not client.is_connected:
            print("Failed to connect to the device.")
            return
        
        await client.start_notify(GYRO_CHAR_UUID, handle_notification)
        await udp_command_task(client)
        
        while True:
            await asyncio.sleep(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    sock_gyro.close()
    sock_cmd.close()
