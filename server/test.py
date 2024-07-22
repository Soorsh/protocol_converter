import socketserver
import time
from galileosky import Packet

HOST = 'localhost'
PORT = 38300


class SimpleTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        headers, tags = Packet.unpack(data)
        self.request.send(Packet.confirm(headers['crc16']))

        buf = bytearray()
        timeout = 10
        t1 = time.time()
        while 1:
            try:
                data = self.request.recv(1024)
            except ConnectionResetError:
                break

            if not data:
                time.sleep(1)
                if t1 + timeout < time.time():
                    break
                continue

            t1 = time.time()

            buf += data

            try:
                headers, tags = Packet.extract(buf)
            except Packet.ExtractPacketFailed:
                continue

            self.request.send(Packet.confirm(headers['crc16']))
            buf = buf[headers['length'] + 5:]


class SimpleTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    request_queue_size = 1000
    daemon_threads = True


if __name__ == "__main__":
    with SimpleTCPServer((HOST, PORT), SimpleTCPRequestHandler) as server:
        server.serve_forever()
