#!/usr/bin/env python3
"""Vercel Python Serverless Function for QQ Bot"""

import json
from http.server import BaseHTTPRequestHandler
import os
import threading
import time

# 模拟机器人运行状态
class BotStatus:
    def __init__(self):
        self.running = True
        self.start_time = time.time()
        self.status = "ok"

    def get_status(self):
        return {
            "status": self.status,
            "running": self.running,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time
        }

# 全局状态
bot_status = BotStatus()

# 模拟机器人线程
def run_bot():
    """模拟机器人运行"""
    while bot_status.running:
        time.sleep(1)

# 启动模拟机器人线程
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# Vercel Python Serverless Function handler
def handler(event, context):
    """Vercel Python Serverless Function handler"""
    path = event["path"]
    method = event["httpMethod"]
    headers = event.get("headers", {})
    
    # 处理健康检查
    if path == "/api/health" and method == "GET":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "ok",
                "message": "Bot is running",
                "bot_info": bot_status.get_status()
            })
        }
    
    # 处理其他API请求
    if path.startswith("/api/"):
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "ok",
                "message": "API endpoint reached",
                "path": path,
                "method": method
            })
        }
    
    # 默认响应
    return {
        "statusCode": 404,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "error",
            "message": "Not found"
        })
    }

# 本地测试用
if __name__ == "__main__":
    # 本地运行时，启动一个简单的HTTP服务器
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            event = {
                "path": self.path,
                "httpMethod": "GET",
                "headers": dict(self.headers)
            }
            response = handler(event, {})
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response["body"].encode())
        
        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            event = {
                "path": self.path,
                "httpMethod": "POST",
                "headers": dict(self.headers),
                "body": body
            }
            response = handler(event, {})
            self.send_response(response["statusCode"])
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response["body"].encode())
    
    from http.server import HTTPServer
    server = HTTPServer(("localhost", 8000), RequestHandler)
    print("Local server running on http://localhost:8000")
    print("Health check: http://localhost:8000/api/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print("Server stopped")
