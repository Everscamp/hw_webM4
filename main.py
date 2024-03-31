from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote_plus
import urllib.parse
from datetime import datetime
from pathlib import Path
import mimetypes
import json
import socket
from threading import Timer


UDP_IP = '127.0.0.1'
UDP_PORT = 5000

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('Content-Length')))
        run_client(UDP_IP, UDP_PORT, data)
        print(f"{unquote_plus(data.decode()) = }")
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
    
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        match pr_url.path:
            case '/':
                self.send_html_file("index.html")
            case '/message':
                self.send_html_file("message.html")
            case _:
                file_path = Path().joinpath(pr_url.path[1:])
                if file_path.exists():
                    self.send_static()
                else:
                    self.send_html_file("error.html", 404)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def save_to_json(self, raw_data):
        data = unquote_plus(raw_data.decode())
        print(data)
        dict_data = {key: value for key, value in [el.split("=") for el in data.split("&")]}
        print(dict_data)
        with open("data/data.json", "a", encoding="utf-8") as f:
            json.dump({str(datetime.now()): dict_data}, f, indent = 6)

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_client(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.sendto(data, server)
    print(f'Send data: {data.decode()} to server: {server}')
    response, address = sock.recvfrom(1024)
    print(f'Response: {response.decode()} from address: {address}')
    sock.close()

def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)

    response = '200'
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            HttpHandler.save_to_json(HttpHandler, data)
            sock.sendto(response.encode(), address)
            print(f'Send: {response} to: {address}')

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    # run()
    # run_server(UDP_IP, UDP_PORT)
    one = Timer(0.1, run)
    one.name = 'First thread'
    one.start()
    two = Timer(0.5, run_server, args=(UDP_IP, UDP_PORT,))
    two.name = 'Second thread'
    two.start()