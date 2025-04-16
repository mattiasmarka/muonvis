import socket
import reader
import json

def control_power(turn_on=True):
    cmd = "f1f2f306010108f4f5f6" if turn_on else "f1f2f306010007f4f5f6"
    send_raw(cmd)


def send_raw(hexstr, port=8900):
    data = bytes.fromhex(hexstr)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        s.connect(("192.168.4.1", port))
        print("Connected... ", end="")
        s.sendall(data)
        print("Sent.")
        try:
            recv = s.recv(1024)
            print("Response (hex):", recv.hex())
            print("Response:", recv)
            return recv
        except:
            print("No response")

def media_play_command(index: int) -> str:
    index_hex = f"{index:02x}"
    second_byte = f"{index + 5:02x}"  # offset
    return f"f1f2f30401{index_hex}{second_byte}f4f5f6"

def angle_cmd(index: int) -> str: # goes to index=116, step irl 0.375 degrees
    index_hex = f"{index:02x}"
    checksum_hex = f"{(index + 0x0B) & 0xFF:02x}"
    return f"f1f2f3090200{index_hex}{checksum_hex}f4f5f6"

def brightness_cmd(level: int) -> str:
    """
    Create a brightness command.
    :param level: 0–100 (brightness percentage)
    :return: hex string to send
    """
    if not (0 <= level <= 255):
        raise ValueError("Brightness must be between 0 and 255")
    b_hex = f"{level:02x}"
    checksum = f"{(level + 0x09) & 0xFF:02x}"
    return f"f1f2f30801{b_hex}{checksum}f4f5f6"

def volume_cmd(level: int) -> str:
    """
    Generate volume control command (0–100).
    """
    if not (0 <= level <= 255):
        raise ValueError("Volume must be between 0–255")
    vol_hex = f"{level:02x}"
    checksum = f"{(level + 0x08) & 0xFF:02x}"
    return f"f1f2f30701{vol_hex}{checksum}f4f5f6"

def play_mode_cmd(mode: str) -> str:
    """
    Generate play mode command.
    :param mode: one of ['loop', 'sequential', 'random', 'once']
    """
    modes = {
        "loop": 0x00,
        "sequential": 0x01,
        "random": 0x02,
        "once": 0x03,
    }
    if mode not in modes:
        raise ValueError("Invalid mode. Use: loop, sequential, random, once")
    val = modes[mode]
    checksum = (val + 0x0B) & 0xFF
    return f"f1f2f30b01{val:02x}{checksum:02x}f4f5f6"

def tone_cmd(mode: str) -> str:
    """
    Generate holofan tone command: 'cold' or 'warm'.
    Returns hex string representing the full protocol message.
    """
    if mode not in ["cold", "warm"]:
        raise ValueError("Tone mode must be 'cold' or 'warm'")

    if mode == "cold":
        tone_payload = [
            {"color": "0"},
            {"r": "21", "g": "21", "b": "16", "l": "0"},
            {"r": "32", "g": "32", "b": "19", "l": "1"},
            {"r": "48", "g": "48", "b": "31", "l": "2"},
            {"r": "64", "g": "64", "b": "37", "l": "3"},
            {"r": "87", "g": "87", "b": "79", "l": "4"},
            {"r": "112", "g": "112", "b": "86", "l": "5"},
            {"r": "135", "g": "135", "b": "90", "l": "6"},
            {"r": "160", "g": "160", "b": "107", "l": "7"},
            {"r": "183", "g": "183", "b": "173", "l": "8"},
            {"r": "207", "g": "207", "b": "140", "l": "9"},
        ]
    else:
        tone_payload = [
            {"color": "1"},
            {"r": "64", "g": "47", "b": "32", "l": "0"},
            {"r": "64", "g": "47", "b": "32", "l": "1"},
            {"r": "88", "g": "71", "b": "40", "l": "2"},
            {"r": "112", "g": "95", "b": "48", "l": "3"},
            {"r": "136", "g": "119", "b": "56", "l": "4"},
            {"r": "160", "g": "143", "b": "64", "l": "5"},
            {"r": "184", "g": "167", "b": "72", "l": "6"},
            {"r": "208", "g": "191", "b": "80", "l": "7"},
            {"r": "232", "g": "215", "b": "88", "l": "8"},
            {"r": "255", "g": "239", "b": "96", "l": "9"},
        ]

    # Encode JSON payload
    json_bytes = json.dumps(tone_payload, separators=(',', ':')).encode('utf-8')

    # Build full protocol message
    header = b'\xf1\xf2\xf3'
    cmd_type = b'\x3d'
    device_id = b'\x01'
    length = len(json_bytes).to_bytes(1, 'big')  # 1-byte length
    footer = b'\xf4\xf5\xf6'

    full_message = header + cmd_type + device_id + length + json_bytes + footer
    return full_message.hex()

def delete_file_cmd(index: int) -> str:
    """
    Create a command to delete file at a given index.
    """
    index_hex = f"{index:02x}"
    return f"f1f2f30101{index_hex}02f4f5f6"


# Try these:
#send_raw("f1f2f306010108f4f5f6") # Turn on
#send_raw("f1f2f306010007f4f5f6") # Turn off

#send_raw("f1f2f3000000f4f5f6")  # Media list/refresh
#reader.show(reader.extract_json_from_response(send_raw("f1f2f3000000f4f5f6"))) # Media list/refresh
#send_raw(media_play_command(6))

#send_raw(angle_cmd(0)) # Angle ctrl


#send_raw("f1f2f30c000cf4f5f6") #Dunno
#send_raw("f1f2f30c000cf4f5f6") #Dunno

#send_raw("f1f2f30401070cf4f5f6") # [7] muoon.mp4
#send_raw("f1f2f30401060bf4f5f6") # [6] saku_PIC.mp4
