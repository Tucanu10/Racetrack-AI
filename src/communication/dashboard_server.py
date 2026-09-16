import os
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler

import serversocket

WEB_DIR = "web"

os.makedirs(os.path.join(WEB_DIR, "assets"), exist_ok=True)
shutil.copy("src/map0/map.png", os.path.join(WEB_DIR, "assets", "map.png"))

ai = serversocket.AICLient(host="localhost", port=8081)


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
        try:
            ack = ai.send_command(command)
            print(f"Command sent: {command} -> {ack}")
            self.send_response(200)
        except Exception as e:
            print(f"Error sending {command}: {e}")
            self.send_response(500)
        self.end_headers()


if __name__ == "__main__":
    print("Dashboard server listening on http://localhost:8000")
    HTTPServer(("localhost", 8000), DashboardHandler).serve_forever()
