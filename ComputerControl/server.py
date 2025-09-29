import platform
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

class HttpServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/system_info":
            self.get_system_info()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def get_system_info(self):
        """只返回当前系统时间"""
        try:
            now = datetime.now().isoformat()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"timestamp": now}).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            msg = f"Error getting system time: {str(e)}".encode()
            self.wfile.write(msg)

    def do_POST(self):
        if self.path != "/shutdown":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        sys_type = platform.system().lower()
        if sys_type == "windows":
            cmd = ["shutdown", "/s", "/t", "0"]
        elif sys_type == "linux" or sys_type == "darwin":
            cmd = ["shutdown", "-h", "now"]
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Unsupported OS")
            return

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Shutdown command executed successfully.")
            else:
                self.send_response(500)
                self.end_headers()
                msg = f"Command failed: {result.stderr}".encode()
                self.wfile.write(msg)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            msg = f"Exception: {str(e)}".encode()
            self.wfile.write(msg)

def run(server_class=HTTPServer, handler_class=HttpServerHandler, port=23009):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
