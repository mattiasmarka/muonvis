import json


def extract_json_from_response(data: bytes) -> dict:
    # Convert bytes to string
    try:
        text = data.decode('utf-8', errors='ignore')

        # Strip off header and footer
        start = text.find('{')
        end = text.rfind('}') + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON found in data")

        json_str = text[start:end]
        parsed = json.loads(f"[{json_str.replace('}{', '},{')}]")  # wrap if it's a list
        return parsed
    except Exception as e:
        print("Error extracting JSON:", e)
        return None

def show(playlist):
    for item in playlist:
        print(f"[{item['sort']}] {item['name']} — {item['size']} bytes")

# # Example usage:
# raw_response = b'\xf1\xf2\xf3\x00\x03\xc7{"name":"Ring.mp4","size":"15880","sort":"0","count":"1","key":"null","status":"0","sum":"684"},{"name":"drones.mp4","size":"16080","sort":"1","count":"1","key":"null","status":"0","sum":"686"}\x03\xf4\xf5\xf6'
#
# playlist = extract_json_from_response(raw_response)
# for item in playlist:
#     print(f"[{item['sort']}] {item['name']} — {item['size']} bytes")
