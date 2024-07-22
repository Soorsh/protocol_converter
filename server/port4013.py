import sys
import socket
import time
import threading
import requests
import queue
import subprocess
import json

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 4013))
server_socket.listen(1)
print("Прослушивается 4013 порт...")

def receive_complete_packet(client_socket):
    client_socket.settimeout(2)
    data = b''
    try:
        while True:
            chunk = client_socket.recv(2048)
            if not chunk:
                client_socket.close()
                break
            data += chunk
            if b'\r\n' in data:
                break
    except socket.timeout:
        #print("Превышен таймаут приема данных.")
        #print("Полученные данные:", data)
        return None
    return data

def process_login_packet(packet, client_socket):
    imei = packet[3:packet.find(';')]
    send_response(client_socket, '#AL#1')
    return imei  # Возвращаем IMEI для использования в дальнейшем

def process_black_box_packet(packet, client_socket, imei):
    packet = packet.replace("#B#", "")
    messages = packet.split('|')

    num_messages = len(messages)
    response_packet = bytes(f'#AB#{num_messages}\r\n', 'utf-8')
    client_socket.send(response_packet)
    print("Отправлено:", response_packet)

    for message in messages:
        if send_decrypted_packet(message, imei):
            print("Сообщение успешно отправлено.")
        else:
            print("Ошибка отправки сообщения.")

def send_response(client_socket, response_code):
    response_packet_bytes = bytes(f'{response_code}\r\n', 'utf-8')
    client_socket.send(response_packet_bytes)
    print("Отправлено:", response_packet_bytes)

def handle_client(client_socket):
    imei = None
    while True:
        packet_bytes = receive_complete_packet(client_socket)

        if packet_bytes:
            packet = packet_bytes.decode('utf-8')
            if packet.startswith('#L#'):
                imei = process_login_packet(packet, client_socket)
            elif packet.startswith('#B#'):
                process_black_box_packet(packet, client_socket, imei)
            else:
                print("Неизвестный тип пакета:", packet)

        else:
            print("Не удалось полностью получить пакет.")
            break

    client_socket.close()
    print("Соединение закрыто.")

def decrypted_packet(packet, imei):
    fields = packet.split(';')

    date = fields[0] if fields[0] != 'NA' else time.strftime("%d%m%y", time.gmtime())
    time_val = fields[1] if fields[1] != 'NA' else time.strftime("%H%M%S", time.gmtime())
    lat = (fields[2], fields[3]) if fields[2] != 'NA' and fields[3] != 'NA' else (0, 0)
    lon = (fields[4], fields[5]) if fields[4] != 'NA' and fields[5] != 'NA' else (0, 0)
    speed = fields[6] if fields[6] != 'NA' else 0
    course = fields[7] if fields[7] != 'NA' else 0
    height = fields[8] if fields[8] != 'NA' else 0
    hdop = fields[10] if fields[10] != 'NA' else 0
    inputs = fields[11] if fields[11] != 'NA' else 0
    outputs = fields[12] if fields[12] != 'NA' else 0
    adc = fields[13] if fields[13] != 'NA' else 0
    ibutton = fields[14] if fields[14] != 'NA' else 0
    params = fields[15] if len(fields) > 15 and fields[15] != 'NA' else 0
    total_sats = 0
    Mdb3 = 0
    Mdb11 = 0

    if params != 0:
        for param in params.split(','):
            if any(sat_system in param for sat_system in ['sats_gps', 'sats_glonass', 'sats_galileo']):
                total_sats += int(param.split(':')[1])
            elif param.startswith("Mdb3:"):
                Mdb3 = param.split(':')[2]
            elif param.startswith("Mdb11:"):
                Mdb11 = param.split(':')[2]

    decrypted_packet = {
        "Дата": date,
        "Время": time_val,
        "Широта": lat,
        "Долгота": lon,
        "Скорость": speed,
        "Курс": course,
        "Высота": height,
        "Снижение точности": hdop,
        "Цифровые входы": inputs,
        "Цифровые выходы": outputs,
        "Аналоговые входы": adc,
        "Код ключа водителя": ibutton,
        "Общее количество спутников": total_sats,
        "Mdb3": Mdb3,
        "Mdb11": Mdb11,
        "Дополнительные параметры": params
    }

    try:
        fuel = str(float(Mdb3) + float(Mdb11))
    except ValueError:
        print(f"Ошибка преобразования Mdb3 ({Mdb3}) и Mdb11 ({Mdb11}) в float.")
        fuel = "0.0"

    status_packet = {
        "imei": imei,
        "height": height,
        "fuel": fuel,
    }

    print("Содержимое status_packet:", status_packet)  # Отладочная информация

    try:
        print("Запуск update_status для", imei)
        subprocess.run(['php', '/var/www/html/backend/elements/update_status.php'], input=json.dumps(status_packet), text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Произошла ошибка при запуске update_status:", e)

    return decrypted_packet

def send_decrypted_packet(packet, imei):
    decrypted_data = decrypted_packet(packet, imei)
    decrypted_packet_with_imei = json.dumps({"imei": imei, "data": decrypted_data})

    try:
        print("Запуск protocol_converter для IMEI:", imei)
        subprocess.run(['php', 'protocol_converter.php'], input=decrypted_packet_with_imei, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("Произошла ошибка при выполнении процесса:", e)
        return False

# Запуск сервера и обработка соединений
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Установлено соединение с {client_address}")

    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()