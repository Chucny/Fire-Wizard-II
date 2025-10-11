# networking.py
import socket
import threading
import json
import time
from queue import Queue

class NetworkConnection:
    """
    Handles safe UDP networking for P2P multiplayer.
    """

    def __init__(self, is_host=True, peer_ip=None, base_port=9999, send_rate=0.05):
        """
        is_host: True if host, False if client
        peer_ip: IP of the other player (required for client)
        base_port: base port number
        send_rate: how often to send player updates
        """
        self.is_host = is_host
        self.peer_ip = peer_ip
        self.base_port = base_port
        self.send_rate = send_rate

        # Set local and peer ports
        if is_host:
            self.local_port = base_port
            self.peer_port = base_port + 1
        else:
            self.local_port = base_port + 1
            self.peer_port = base_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.sock.bind(('', self.local_port))

        self.running = True
        self.peer_addr = (peer_ip, self.peer_port) if peer_ip else None
        self.incoming = Queue()

        # Start receive thread
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()

    def _recv_loop(self):
        """Continuously receive data and put into queue."""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
            except socket.timeout:
                continue
            except Exception:
                continue

            # Auto-set peer_addr if unknown
            if not self.peer_addr:
                self.peer_addr = addr
                # Send handshake back
                self.safe_send({'type':'hello'})
                print(f"[network_lib] Connected to {self.peer_addr}")

            try:
                msg = json.loads(data.decode())
                self.incoming.put(msg)
            except:
                pass

    def safe_send(self, msg: dict):
        """Send a message safely to the peer."""
        if not self.peer_addr:
            return
        try:
            self.sock.sendto(json.dumps(msg).encode(), self.peer_addr)
        except:
            pass

    def safe_receive(self):
        """Return one packet from the queue, or None."""
        if not self.incoming.empty():
            return self.incoming.get()
        return None

    def close(self):
        """Stop networking safely."""
        self.running = False
        try:
            self.sock.close()
        except:
            pass
