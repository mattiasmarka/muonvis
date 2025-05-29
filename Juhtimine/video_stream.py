import time
import zipfile
import os
import json
import http.server
import socketserver
import threading
import commands
import subprocess
from Connection import HoloFanClient

def get_mp4_duration_ms(file_path: str) -> int:
    """
    Returns the duration of an MP4 file in milliseconds using ffprobe.
    """
    result = subprocess.run([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        seconds = float(result.stdout.strip())
        return int(seconds * 1000)
    except Exception as e:
        print("Error reading duration:", e)
        return 0

def add_mp4_to_zip(mp4_file_path, zip_file_path='test_PIC.zip'):
    """
    Adds an MP4 file to a ZIP archive named test_PIC.zip.
    """
    if not os.path.isfile(mp4_file_path):
        raise FileNotFoundError(f"{mp4_file_path} does not exist.")

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        zipf.write(mp4_file_path, arcname=os.path.basename(mp4_file_path))
    print(f"Added {mp4_file_path} to {zip_file_path}")




def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't need to be reachable — it's used for routing decision
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def upload_media_cmd(url: str, name: str, size: int, time: int) -> str:
    header = b'\xf1\xf2\xf3'
    cmd = b'\x17\x00'

    # URL part
    url_bytes = b'\x6d\x06' + b'{' + url.encode('utf-8') + b'}'

    # JSON body with binary values
    body = b'{'
    body += b'size:' + size.to_bytes(4, 'big') + b','       # raw 4-byte int
    body += b'name:"' + name.encode('utf-8') + b'",'
    body += b'time:' + time.to_bytes(4, 'big') + b','       # raw 4-byte int
    body += b'"song":"' + name.encode('utf-8') + b'"}'

    # Join pieces
    payload = url_bytes + body

    # Compute checksum as sum of all payload bytes mod 256
    checksum = sum(payload) % 256
    checksum_byte = checksum.to_bytes(1, 'big')

    footer = b'\xf4\xf5\xf6'
    full = header + cmd + payload + checksum_byte + footer

    return full.hex()






if __name__ == "__main__":
    mp4_file = "proov3_PIC.mp4"  # <-- replace with your .mp4 file
    zip_file = "proov2_PIC.zip"
    directory = 'Video/'
    port = 8080
    ip = get_local_ip()
    url = f"http://{ip}:{port}/{zip_file}"

    mp4_time = get_mp4_duration_ms(directory+mp4_file)

    # 1. Zip the mp4
    #add_mp4_to_zip(directory+mp4_file, directory+zip_file)
    zip_size = os.path.getsize(directory+zip_file)



    # 2. Start TDP connection
    client = HoloFanClient()
    client.connect()


    # 3. Create upload hex command
    upload_hex = upload_media_cmd(
        url=url,
        name=zip_file,
        size=zip_size,
        time=mp4_time
    )

    print(f"Upload hex: {upload_hex}")
    print(url)

    time.sleep(1)

    client.send_raw("aa00000002f000a5") # Dunno
    time.sleep(1)
    client.send_raw("f1f2f30c000cf4f5f6") # Dunno
    time.sleep(1)
    client.send_raw("f1f2f3130013f4f5f6") # account
    time.sleep(1)
    client.send_raw("f1f2f3120012f4f5f6") # MCU
    time.sleep(1)
    client.send_raw("f1f2f32c002cf4f5f6") # CS_Box
    time.sleep(1)
    client.send_raw("f1f2f3000000f4f5f6") # Media list


    time.sleep(1)
    while True:
        time.sleep(1)
        inp = input("[Send command]\n")

        if inp == "4":
            client.send_raw(commands.media_play_command(int(input("[Media #]\n"))))

        if inp == "5":
            client.send_raw(commands.angle(int(input("[Angle 0-116]\n"))))

        if inp == "on":
            client.send_raw("f1f2f306010108f4f5f6")

        if inp == "off":
            client.send_raw("f1f2f306010007f4f5f6")

        if inp == "3":
            client.send_raw(upload_hex)

        if inp == "2":
            client.send_raw("aa00000002f000a5")
            time.sleep(1)
            client.send_raw("f1f2f30c000cf4f5f6")
            time.sleep(1)
            client.send_raw("f1f2f3130013f4f5f6")  # account
            time.sleep(1)
            client.send_raw("f1f2f3120012f4f5f6")  # MCU
            time.sleep(1)
            client.send_raw("f1f2f32c002cf4f5f6")  # CS_Box
            time.sleep(1)
            client.send_raw("f1f2f3000000f4f5f6")  # Media list

        if inp == "1":
            client.send_raw("f1f2f3000000f4f5f6")

        if inp == "0":
            #httpd.shutdown()
            client.close()
            exit(0)
