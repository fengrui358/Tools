import sys
import os
import platform
import psutil
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
        """获取系统硬件信息"""
        try:
            # 系统基本信息
            system_info = {
                "timestamp": datetime.now().isoformat(),
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "hostname": platform.node()
            }
            
            # CPU信息
            cpu_info = {
                "cpu_cores": psutil.cpu_count(logical=False),
                "cpu_threads": psutil.cpu_count(logical=True),
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
            
            # 内存信息
            memory = psutil.virtual_memory()
            memory_info = {
                "total_memory_gb": round(memory.total / (1024**3), 2),
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "used_memory_gb": round(memory.used / (1024**3), 2),
                "memory_usage_percent": memory.percent
            }
            
            # 磁盘信息
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "usage_percent": usage.percent
                    })
                except PermissionError:
                    continue
            
            # 网络信息
            net_info = psutil.net_io_counters()
            network_info = {
                "bytes_sent": net_info.bytes_sent,
                "bytes_recv": net_info.bytes_recv,
                "packets_sent": net_info.packets_sent,
                "packets_recv": net_info.packets_recv
            }
            
            # 系统运行时间
            boot_time = psutil.boot_time()
            uptime_info = {
                "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
                "uptime_seconds": int(datetime.now().timestamp() - boot_time)
            }
            
            # 组合所有信息
            all_info = {
                "system": system_info,
                "cpu": cpu_info,
                "memory": memory_info,
                "disks": disk_info,
                "network": network_info,
                "uptime": uptime_info
            }
            
            # 返回JSON响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(all_info, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            msg = f"Error getting system info: {str(e)}".encode()
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
