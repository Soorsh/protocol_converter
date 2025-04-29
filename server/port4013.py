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
    return imei

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
            print("Ветроятно сообщение не подошло и небыло отправлено в базу данных.")

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

    params_dict = {}
    if params and isinstance(params, str):
        for param in params.split(','):
            try:
                name, param_type, value = param.split(':')
                if param_type == '1':
                    params_dict[name] = int(value)
                elif param_type == '2':
                    params_dict[name] = float(value)
                elif param_type == '3':
                    params_dict[name] = value
            except ValueError:
                print(f"Ошибка при разборе параметра: {param}")

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
        "Код ключа водителя": ibutton
    }

    # Обработка параметров Mdb и добавление в decrypted_packet__________________________________________________________
    if not any(key.startswith("Mdb") for key in params_dict):
        print("фкнция decrypted_packet завершается: return None")
        return None
    for i in range(7):
        param_name = ["уровень топлива", "температура топлива", "процент заполнения", "общий объем топлива", "масса топлива", "плотность топлива", "основной объем топлива"][i]
        total_sum = 0
        valid_values_count = 0
        for j in range(4):
            mdb_key = i + j * 8
            key = f"Mdb{mdb_key}"
            if key in params_dict:
                value = params_dict[key]
                if value != 0:
                    total_sum += value
                    valid_values_count += 1
                del params_dict[key]
        if valid_values_count > 0:
            decrypted_packet[param_name] = total_sum / valid_values_count

    # Обработка параметров Amx и добавление в decrypted_packet__________________________________________________________
    amx_params_description = {
        "Amx0": {
            1: "запрос данных карты с сервера",
            10: "авторизация выполнена, переход в ожидание ввода дозы пролива",
            11: "успешная авторизация карты, баланс получен",
            12: "авторизация незарегистрированной карты",
            13: "авторизация заблокированной карты",
            14: "авторизация на заблокированной ТРК",
            2: "введена доза, ТРК приняла дозу, ожидание старта",
            21: "передача дозы в ТРК",
            4: "зафиксирована заправка",
            51: "переход в режим ожидания по таймауту ввода дозы",
            52: "переход в режим ожидания по таймауту получения баланса",
            53: "пользователь отменил авторизацию",
            6: "изменен статус ТРК",
            1000: "сообщение по времени"
        },
        "Amx1": {
            0: "ожидание",
            1: "запрос данных карты с сервера",
            10: "авторизация карты, баланс успешно получен",
            11: "авторизация карты, ошибка на сервере",
            12: "авторизация карты, незарегистрированная карта",
            13: "авторизация карты, карта заблокирована",
            14: "авторизация карты, ТРК заблокирована",
            2: "доза введена, ожидание старта ТРК",
            21: "передача дозы в ТРК",
            3: "пролив топлива",
            4: "пролив окончен, фиксация заправки"
        },
        "Amx10": {
            0: "ТРК в режиме ожидания, кран установлен",
            1: "ТРК в режиме ожидания, кран снят",
            2: "установлена доза пролива, ожидание старта ТРК",
            3: "работа ТРК, пролив топлива",
            4: "зафиксирована заправка, окончание пролива"
        },
    }

    key_translation = {
        "Amx0": "Причина отсылки сообщения",
        "Amx1": "Режим работы МОДУЛЯ",
        "Amx2": "Номер карты",
        "Amx3": "Баланс карты на момент авторизации",
        "Amx4": "Введенная доза пролива",
        "Amx5": "Текущий счетчик ТРК",
        "Amx6": "Объем зафиксированной заправки",
        "Amx7": "Нач. тотальный счетчик перед заправкой",
        "Amx8": "Кон. тотальный счетчик после заправки",
        "Amx10": "Статус ТРК",
        "Amx11": "Тотальный (суммарный) счетчик ТРК",
    }

    # Обработка параметров Amx и добавление в decrypted_packet
    for key in amx_params_description.keys():
        if key in params_dict:
            value = params_dict[key]
            if value in amx_params_description[key]:
                decrypted_packet[key_translation[key]] = amx_params_description[key][value]
            del params_dict[key]

    # Обработка остальных ключей
    for key, value in params_dict.items():
        if key == "Amx2":
            decrypted_packet[key_translation[key]] = value
        elif key == "Amx3":
            decrypted_packet[key_translation[key]] = value
        elif key == "Amx4":
            decrypted_packet[key_translation[key]] = value
        elif key == "Amx5":
            decrypted_packet[key_translation[key]] = value * 0.01
        elif key == "Amx6":
            decrypted_packet[key_translation[key]] = value * 0.01
        elif key == "Amx7":
            decrypted_packet[key_translation[key]] = value * 0.01
        elif key == "Amx8":
            decrypted_packet[key_translation[key]] = value * 0.01
        elif key == "Amx11":
            decrypted_packet[key_translation[key]] = value * 0.01

    # Обработка параметров GPS и добавление в decrypted_packet__________________________________________________________
    additional_params = {
        "status": "статус",
        "sats_gps": "спутники gps",
        "sats_glonass": "спутники glonass",
        "sats_galileo": "спутники galileo",
        "pwr_ext": "внешнее питание",
        "pwr_akb": "аккумулятор",
        "rssi": "уровень сигнала",
        "bootcount": "количество перезагрузок",
    }
    for param in additional_params.keys():
        if param in params_dict:
            decrypted_packet[additional_params[param]] = params_dict[param]
            del params_dict[param]

    # Формируем статус пакет____________________________________________________________________________________________
    status_packet = {
        "imei": imei,
        "height": height,
        "fuel": decrypted_packet.get("уровень топлива", 0),
    }

    try:
        print("Запуск update_status для", imei)
        subprocess.run(['php', '/var/www/html/backend/elements/update_status.php'], input=json.dumps(status_packet), text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Произошла ошибка при запуске update_status:", e)
    return decrypted_packet

def send_decrypted_packet(packet, imei):
    decrypted_data = decrypted_packet(packet, imei)
    if decrypted_data is None:
            imei = None
            return False

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