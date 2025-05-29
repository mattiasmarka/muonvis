import socket
import threading


class HoloFanClient:
    def __init__(self, ip="192.168.4.1", port=8900, timeout=1.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.running = False
        self.recv_thread = None

    def connect(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.ip, self.port))
            self.running = True
            self.recv_thread = threading.Thread(target=self.receive_loop, daemon=True)
            self.recv_thread.start()
            print("Connected to HoloFan.")

    def receive_loop(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if data:
                    print("[Incoming] Response (hex):", data.hex())
                    print("[Incoming] Response:", data)
            except socket.timeout:
                continue
            except OSError:
                break  # Socket closed
            except Exception as e:
                print("Error in receive loop:", e)
                break

    def send_raw(self, hexstr):
        if self.sock is None:
            raise RuntimeError("Not connected. Call connect() first.")

        data = bytes.fromhex(hexstr)
        print("Sending... ", end="")
        self.sock.send(data)
        print(f"Sent: {hexstr}")

    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.sock.close()
            self.sock = None
            print("Connection closed.")

# Example usage:
# client = HoloFanClient()
# client.connect()
# client.send_raw("f1f2f3...")
# # Will print incoming messages automatically
# client.close()
