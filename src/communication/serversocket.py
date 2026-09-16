import socket
import threading
import time

import engine.config as config

class AICLient:
    def __init__(self, host='localhost', port=config.COMMUNICATION_PORT, retry_interval=1.0):
        
        self.sock = None
        while self.sock is None:
            candidate = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                candidate.connect((host, port))
                self.sock = candidate
            except (ConnectionRefusedError, OSError):
                candidate.close()
                print(f"Waiting for Java server at {host}:{port}...")
                time.sleep(retry_interval)
        self._lock = threading.Lock()

    def _recv_until_newline(self):
        response = ""
        while not response.endswith("\n"):
            chunk = self.sock.recv(4096).decode('utf-8')
            if not chunk:
                break
            response += chunk
        return response.strip()

    def get_batch_commands(self, payload):
        with self._lock:
            self.sock.sendall((payload + "\n").encode('utf-8'))
            response = self._recv_until_newline()

        commands = {}
        if not response:
            return commands

        for entry in response.split('|'):
            cid, vals = entry.split(':')
            parts = [float(p) for p in vals.split(',')]
            st = parts[0]
            th = parts[1]

            # parts[2] is the number of hidden layers, then each layer is
            # prefixed with its own size: [size0, v0_0, v0_1, ..., size1, ...]
            hidden_layers = []
            cursor = 3
            num_layers = int(parts[2]) if len(parts) > 2 else 0
            for _ in range(num_layers):
                layer_size = int(parts[cursor])
                cursor += 1
                hidden_layers.append(parts[cursor:cursor + layer_size])
                cursor += layer_size

            commands[int(cid)] = (st, th, hidden_layers)
            
        return commands
    
    def send_epoch_end(self, scores):
        payload = "EPOCH_END:" + ",".join(map(str, scores)) + "\n"
        with self._lock:
            self.sock.sendall(payload.encode('utf-8'))
            return self._recv_until_newline()

    def send_command(self, command):
        with self._lock:
            self.sock.sendall((command + "\n").encode('utf-8'))
            return self._recv_until_newline()

    def close(self):
        self.sock.close()