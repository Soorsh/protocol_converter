import socket
from galileosky import Packet, tags
import libscrc

def send_confirmation_packet(client_socket, packet_bytes):
    confirmation_packet = Packet.confirm(libscrc.modbus(packet_bytes))
    client_socket.sendall(confirmation_packet)
    print(f"Отправлен пакет подтверждения: {confirmation_packet}\n")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 4012))
server_socket.listen(1)
print("Прослушивается 4012 порт...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Подключен клиент: {client_address}\n")

    while True:
        packet_bytes = client_socket.recv(2048)

        if packet_bytes:
            print(f"\nПолучен пакет: {packet_bytes}\n")
            headers, packet_data = Packet.unpack(packet_bytes)
            send_confirmation_packet(client_socket, packet_bytes)  # Отправляем подтверждение приема пакета

            print("Headers:", headers)
            print("Packet data:", packet_data)
        else:
            print("\nСоединение было закрыто.")
            break

    client_socket.close()
    print("Переходим к следующему соединению.")
