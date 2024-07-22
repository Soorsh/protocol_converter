import json
import pymysql
import random
import config
import socket
import struct
import time
import pymysql.err
from datetime import datetime, timedelta
from galileosky import Packet

def create_galileosky_packet(data, connection, id):
    json_data = json.loads(data)
    cursor = connection.cursor()
    message_sent = None

    packet = Packet()
    imei_data = json_data.get('imei')
    packet.add(0x03, dict(imei=imei_data))
    packed_packet, crc16 = packet.pack()
    imei = imei_data
    #HOST = 'localhost'
    #PORT = 4050

    HOST = '212.77.128.8'
    PORT = 4010
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                while True:
                    try:
                        s.sendall(packed_packet)
                        print(packed_packet)
                        recv_data = s.recv(1024)
                        # print(recv_data)
                    except socket.error as e:
                            print(f"Ошибка сетевого соединения: {e}")
                            time.sleep(15)

                    received_checksum = struct.unpack('<H', recv_data[1:3])[0]
                    message_sent = True
                    if received_checksum == crc16:
                        break
                    else:
                        print("Ошибка: Контрольные суммы не совпадают.")
                        time.sleep(15)

                while True:
                    while message_sent:
                        json_data = json.loads(data)
                        data_SQL = data
                        main_packet = Packet()

                        # tag time № 20
                        time_data = json_data["data"]["Время"]
                        date_data = json_data["data"]["Дата"]
                        time_obj = datetime.strptime(time_data, "%H%M%S")
                        date_obj = datetime.strptime(date_data, "%d%m%y")
                        time_obj += timedelta(hours=0)
                        date_time = datetime.combine(date_obj.date(), time_obj.time())
                        main_packet.add(0x20, dict(time=int((date_time - datetime(1970, 1, 1)).total_seconds())))

                        # tag velocity № 33
                        speed = int(json_data["data"]["Скорость"])
                        course = int(json_data["data"]["Курс"])
                        main_packet.add(0x33, {'speed': speed, 'course': course})

                        # tag height № 34
                        main_packet.add(0x34, dict(height=int(json_data["data"]["Высота"])))

                        # tag height № DC
                        #can32bitr1_data = float(json_data["data"]["Mdb3"]) + float(json_data["data"]["Mdb11"])
                        #can32bitr1_data = can32bitr1_data * 1000
                        #main_packet.add(0xDC, dict(can32bitr1=can32bitr1_data))

                        # tag height № DD
                        can32bitr2_data = float(json_data["data"]["Mdb3"]) + float(json_data["data"]["Mdb11"])
                        can32bitr2_data = can32bitr2_data * 1000
                        main_packet.add(0xDD, dict(can32bitr2=can32bitr2_data))

                        # расмотреть тег 0x60-15?

                        packed_packet, crc16 = main_packet.pack()

                        print(packed_packet)

                        while True:
                            s.sendall(packed_packet)
                            data = s.recv(1024)
                            # print(data)
                            received_checksum = struct.unpack('<H', data[1:3])[0]
                            if received_checksum == crc16:
                                sql = f"DELETE FROM PacketLogs WHERE packet_id = '{id}'"
                                cursor.execute(sql)
                                connection.commit()
                                message_sent = False
                                break
                            else:
                                print("Ошибка: Контрольные суммы не совпадают.")
                                time.sleep(15)

                    cursor.execute(f"SELECT packet_id, raw_data FROM PacketLogs WHERE sent_status IS NULL AND imei = '{imei}' LIMIT 1")
                    data_row = cursor.fetchone()
                    if data_row:
                        data = data_row['raw_data']
                        id = data_row['packet_id']
                        message_sent = True
                    else:
                        return

        except Exception as e:
            print("Ошибка:", e)
            time.sleep(15)

def handle_database_data():
    while True:
        connection = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASS,
            database=config.DB_NAME,
            charset=config.DB_CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                sql = "SELECT packet_id, raw_data FROM PacketLogs WHERE sent_status IS NULL LIMIT 1"
                cursor.execute(sql)
                data_row = cursor.fetchone()
                if data_row:
                    data = data_row['raw_data']
                    id = data_row['packet_id']
                    create_galileosky_packet(data, connection, id)
                else:
                    print("В БД нет сообщений")
                    time.sleep(10)

        except Exception as e:
            print("Ошибка при обработке данных из базы данных:", e)
            sleep(15)
        finally:
            connection.close()

def start_server():
    print("Сервер запущен. Ожидание данных из БД...")
    try:
        handle_database_data()

    except KeyboardInterrupt:
        print("Сервер остановлен.")

if __name__ == "__main__":
    start_server()
