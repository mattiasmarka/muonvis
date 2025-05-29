import json


def show_playlist(data: bytes):
    # Convert bytes to string
    try:
        text = data.decode('utf-8', errors='ignore')

        # Strip off header and footer
        start = text.find('{')
        end = text.rfind('}') + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON found in data")

        json_str = text[start:end]
        playlist = json.loads(f"[{json_str.replace('}{', '},{')}]")  # wrap if it's a list

        if playlist is None: return None
        for item in playlist:
            print(f"[{item['sort']}] {item['name']} — {item['size']} bytes")

    except Exception as e:
        print("Error extracting JSON:", e)
        return None


def media_play_command(index: int) -> str:
    header = b'\xf1\xf2\xf3'
    footer = b'\xf4\xf5\xf6'

    # Construct payload
    cmd_id = b'\x04\x01'
    idx_byte = index.to_bytes(1, 'big')
    offset_byte = (index + 5).to_bytes(1, 'big')
    payload = cmd_id + idx_byte + offset_byte

    # Calculate checksum
    checksum = sum(payload) % 256
    checksum_byte = checksum.to_bytes(1, 'big')

    # Construct full packet
    full_packet = header + payload + checksum_byte + footer
    return full_packet.hex()


def angle(index: int) -> str:
    # Constant header and footer
    header = b'\xf1\xf2\xf3'
    footer = b'\xf4\xf5\xf6'

    # Payload without checksum
    cmd_id = b'\x09\x02\x00'
    idx_byte = index.to_bytes(1, 'big')
    payload = cmd_id + idx_byte

    # Compute checksum as sum of payload bytes mod 256
    checksum = sum(payload) % 256
    checksum_byte = checksum.to_bytes(1, 'big')

    # Combine everything
    full_packet = header + payload + checksum_byte + footer
    return full_packet.hex()


def brightness(level: int) -> str:
    if not (0 <= level <= 100):
        raise ValueError("Brightness must be between 0 and 255")

    header = b'\xf1\xf2\xf3'
    footer = b'\xf4\xf5\xf6'

    cmd_id = b'\x08\x01'
    level_byte = level.to_bytes(1, 'big')
    payload = cmd_id + level_byte

    # Calculate checksum
    checksum = sum(payload) % 256
    checksum_byte = checksum.to_bytes(1, 'big')

    full_packet = header + payload + checksum_byte + footer
    return full_packet.hex()


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


def delete_file_cmd(index: int) -> str:
    header = b'\xf1\xf2\xf3'
    footer = b'\xf4\xf5\xf6'

    cmd_id = b'\x01\x01'
    index_byte = index.to_bytes(1, 'big')
    constant_byte = b'\x02'
    payload = cmd_id + index_byte + constant_byte

    checksum = sum(payload) % 256
    checksum_byte = checksum.to_bytes(1, 'big')

    full_packet = header + payload + checksum_byte + footer
    return full_packet.hex()


def build_bulk_config(status_dict: dict) -> str:
    """
    Constructs a HoloFan bulk status/config command.

    Args:
        status_dict (dict): Keys are strings like "0", "1", ..., values are strings like "1".

    Returns:
        bytes: Complete command ready to send.
    """
    header = b'\xf1\xf2\xf3'
    command_id = b'\x1b'  # Command ID for bulk config (from your capture)

    # Serialize each key-value pair as a separate JSON object and join with commas
    json_items = [json.dumps({k: v}) for k, v in status_dict.items()]
    payload_str = ",".join(json_items)
    payload_bytes = payload_str.encode("utf-8")

    # Length (2 bytes, big-endian)
    length_bytes = len(payload_bytes).to_bytes(2, byteorder='big')

    # Build the message before checksum
    message_body = command_id + length_bytes + payload_bytes

    # Compute checksum over message_body
    checksum = sum(message_body) % 256
    checksum_byte = checksum.to_bytes(1, byteorder='big')

    footer = b'\xf4\xf5\xf6'

    # Final packet
    full = header + message_body + checksum_byte + footer
    return full.hex()
