import os
import sys
import shutil
<<<<<<< HEAD
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import serversocket
import engine.config as config
=======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from http.server import HTTPServer, SimpleHTTPRequestHandler

import serversocket
import config

WEB_DIR = "web"

os.makedirs(os.path.join(WEB_DIR, "assets"), exist_ok=True)
shutil.copy(f"src/{config.ACTIVE_MAP}/map.png", os.path.join(WEB_DIR, "assets", "map.png"))
shutil.copy("images/car.png", os.path.join(WEB_DIR, "assets", "car.png"))
shutil.copy("images/car_best.png", os.path.join(WEB_DIR, "assets", "car_best.png"))
shutil.copy("images/car_worst.png", os.path.join(WEB_DIR, "assets", "car_worst.png"))

ai = None

def get_ai():
    global ai
    if ai is None:
        try:
            ai = serversocket.AICLient(host="localhost", port=config.COMMUNICATION_PORT, max_retries=3)
        except Exception as e:
            print(f"Could not connect to AI server: {e}")
    return ai

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/save":
            self._send_command("SAVE")
        elif self.path == "/load":
            self._send_command("LOAD")
        elif self.path == "/reset":
            self._send_command("RESET")
        else:
            super().do_GET()

    def log_message(self, format, *args):
        if self.path.startswith("/state.json") or self.path.startswith("/assets/"):
            return
        super().log_message(format, *args)

    def _send_command(self, command):
        client = get_ai()
        if client is None:
            self.send_response(503)
            self.end_headers()
            return
        try:
            ack = client.send_command(command)
            print(f"Command sent: {command} -> {ack}")
            if command == "RESET":
                signal_path = os.path.join(WEB_DIR, "reset.signal")
                open(signal_path, "w").close()
            self.send_response(200)
        except Exception as e:
            print(f"Error sending {command}: {e}")
            self.send_response(500)
        self.end_headers()

class DaemonHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    print("Dashboard server listening on http://localhost:" + str(config.DASH_PORT))
    
    # 4. Use the new DaemonHTTPServer instead of HTTPServer
    httpd = DaemonHTTPServer(("", config.DASH_PORT), DashboardHandler)
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, Exception) as e:
        print(f"Shutting down dashboard server due to: {e}")
        httpd.server_close()
        sys.exit(0)