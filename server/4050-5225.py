import socketserver
import time
from galileosky import Packet

HOST = '0.0.0.0'
PORT = 4050  # изменён порт на 4050

class SimpleTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Connection established with {self.client_address}")
        data = self.request.recv(1024)
        headers, tags = Packet.unpack(data)
        self.request.send(Packet.confirm(headers['crc16']))

        print("Received initial packet: Headers -", headers, "; Tags -", tags)

        buf = bytearray()
        timeout = 10
        t1 = time.time()
        while True:
            try:
                data = self.request.recv(1024)
                print(f"Received {len(data)} bytes of data.")
            except ConnectionResetError:
                print("Connection was reset by the client.")
                break

            if not data:
                print("No data received. Waiting...")
                time.sleep(1)
                if t1 + timeout < time.time():
                    print("Connection timed out.")
                    break
                continue

            t1 = time.time()
            buf += data

            try:
                headers, tags = Packet.extract(buf)
                print("Extracted packet: Headers -", headers, "; Tags -", tags)
                self.request.send(Packet.confirm(headers['crc16']))
                buf = buf[headers['length'] + 5:]
            except Packet.ExtractPacketFailed:
                print("Failed to extract packet. Continuing to accumulate data.")
                continue

        print("Session with client ended.")

class SimpleTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    request_queue_size = 1000
    daemon_threads = True

if __name__ == "__main__":
    with SimpleTCPServer((HOST, PORT), SimpleTCPRequestHandler) as server:
        print("Server started on port", PORT)
        server.serve_forever()
