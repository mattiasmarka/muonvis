# Holofan Control via Python

Reverse-engineered Python interface for controlling a CS-X56 Holofan over Wi-Fi using custom commands, based on network packet analysis and app decompilation.

## 📡 How It Works

The fan receives commands via TCP on port `8900`. Each command has a structure:

```
Header:      f1f2f3
Command ID:  varies (e.g. 06 for power, 04 for play)
Payload:     command-specific
Footer:      f4f5f6
```

Example (turn fan on):
```
f1f2f306010108f4f5f6
```

## 📂 Example Commands

```python
def fan_on_cmd() -> str:
    return "f1f2f306010108f4f5f6"

def media_play_cmd(index: int) -> str:
    index_hex = f"{index:02x}"
    second_byte = f"{index + 5:02x}"
    return f"f1f2f30401{index_hex}{second_byte}f4f5f6"
```

## 🛰️ Media Upload Example
Not working.

```python
def upload_media_cmd(url: str, name: str, size: int, time: int = 0x1fc62c) -> str:
    header = b'\xf1\xf2\xf3'
    cmd = b'\x17\x00'
    url_bytes = b'\x6d\x06' + b'{' + url.encode() + b'}'
    body = b'{size:' + size.to_bytes(4, 'big') + b','            + b'name:"' + name.encode() + b'",'            + b'time:' + time.to_bytes(4, 'big') + b','            + b'song:"' + name.encode() + b'"}'
    full = header + cmd + url_bytes + body + b'\xf4\xf5\xf6'
    return full.hex()
```

## 🧪 How to Use

1. **Wi-Fi:** Connect to the Holofan hotspot
2. **Start Python Script:** Main script is `video_stream.py`
4. **Capture Traffic:** Analyze with Wireshark to refine commands

## 🧠 Reverse Engineering Notes

- App uses a fixed structure for commands, padded and with checksums
- File uploads are `.zip` with `.mp4` inside — the fan does polar transformation internally
- Wi-Fi can only have **one active client** at a time — enforced in firmware
- Attempts for root or SSH access briefly explored via UART and flash memory (KLM461FETE)

