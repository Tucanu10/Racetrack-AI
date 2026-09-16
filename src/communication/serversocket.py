import socket

class AICLient:
    def __init__(self, host='localhost', port=8080): # Corrected port to 8080
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def _recv_until_newline(self):
        response = ""
        while not response.endswith("\n"):
            chunk = self.sock.recv(4096).decode('utf-8')
            if not chunk:
                break
            response += chunk
        return response.strip()

    def get_batch_commands(self, payload):
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
        self.sock.sendall(payload.encode('utf-8'))
        return self._recv_until_newline()

    def close(self):
        self.sock.close()