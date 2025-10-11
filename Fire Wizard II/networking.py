# networking.py
import socket
import json
import threading
import time

class NetworkConnection:
    def __init__(self, is_host=True, peer_ip=None, base_port=9999):
        self.is_host = is_host
        self.peer_ip = peer_ip

        # Assign ports safely
        self.local_port = base_port if is_host else base_port + 1
        self.peer_port = base_port + 1 if is_host else base_port

        self.peer_addr = None if is_host else (peer_ip, self.peer_port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow reuse
        self.sock.settimeout(0.05)  # non-blocking

        try:
            self.sock.bind(('', self.local_port))
            print(f"Socket bound to port {self.local_port}")
        except OSError as e:
            print(f"Socket bind failed on port {self.local_port}: {e}")

        self.running = False
        self.incoming_queue = []

    def start(self):
        self.running = True
        threading.Thread(target=self.recv_loop, daemon=True).start()

    def recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                if self.is_host and not self.peer_addr:
                    self.peer_addr = addr
                    print("Client connected:", addr)
                try:
                    msg = json.loads(data.decode())
                    self.incoming_queue.append(msg)
                except Exception:
                    pass
            except Exception:
                time.sleep(0.01)

    def safe_receive(self):
        if self.incoming_queue:
            return self.incoming_queue.pop(0)
        return None

    def safe_send(self, msg):
        if self.peer_addr:
            try:
                self.sock.sendto(json.dumps(msg).encode(), self.peer_addr)
            except Exception:
                pass

    def close(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass
