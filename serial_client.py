from ws4py.client.threadedclient import WebSocketClient
import serial
import json
import threading
# import codecs
# from datetime import datetime
# import time
import sys
# Unixシェルのパス検索モジュール
import glob
import subprocess


class SerialWs(WebSocketClient):
    serial_thread = None

    def opened(self):
        print("serial_client_opend")
        pass

    def closed(self, code, reason=None):
        print("serial_client_closed")
        # pass

    def received_message(self, message):
        # print(message.data)
        data = json.loads(message.data.decode('utf-8'))
        print(data)
        if data["type"] == "send":
            self.serial_thread.send_message(data["message"])
        elif data["type"] == "open":
            self.serial_thread = SerialThread(
                data["port"],
                data["baudrate"],
                data["databit"],
                data["stopbit"],
                data["parity"],
                self
            )
            self.serial_thread.setDaemon(True)
            self.serial_thread.start()
        elif data["type"] == "close":
            self.serial_thread.stop()
        elif data["type"] == "exit":
            subprocess.check_output('killall - KILL SerialTool', shell=True)
            sys.exit()
        else:
            pass


# シリアルスレッドクラス
class SerialThread(threading.Thread):
    def __init__(self, port, baudrate, databit, stopbit, parity, ws):
        super(SerialThread, self).__init__()
        self.stop_event = threading.Event()
        self.port = port
        self.baudrate = int(baudrate)
        self.databit = int(databit)
        self.stopbit = int(stopbit)
        self.parity = parity
        self.ws = ws
        self.serial_port = None

    def stop(self):
        self.stop_event.set()

    def send_message(self, message):
        self.serial_port.reset_output_buffer()
        self.serial_port.write(message.encode('utf-8').decode('unicode_escape').encode('utf-8'))
        # self.serial_port.write(message.encode('utf-8'))

    def run(self):
        try:
            # ポートが閉じた時のエラー処理も欲しい
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.databit,
                parity=self.parity,
                stopbits=self.stopbit,
                timeout=0
            )
            # ポート起動完了通知
            self.ws.send(json.dumps({
                "type":"status",
                "status":"connected",
                "condition": self.port + "/" + str(self.databit) + "/" + str(self.stopbit) + "/" + self.parity
            }))
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            # スレッド終了イベントが来るまでメイン処理
            while not self.stop_event.is_set():
                # time.sleep(0.1)
                reading = self.serial_port.read()
                if len(reading) != 0:
                    # print(reading)
                    try:
                        data = {}
                        data["type"] = "data"
                        # data["name"] = self.port
                        if reading == b'\n':
                            data["data"] = '0x%02x' % ord(reading.decode('utf-8')) + "\n"
                        else:
                            data["data"] = '0x%02x' % ord(reading.decode('utf-8')) + ","
                        # data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        # print(json.dumps(data))
                        self.ws.send(json.dumps(data, ensure_ascii=False))
                    except ValueError as error:
                        self.ws.send(json.dumps({"type":"error","error":"decode error"}))
            self.ws.send(json.dumps({"type":"status","status":"disconnected","device":self.port}))
        # エラー処理
        except ValueError as error:
            self.ws.send(json.dumps({"type":"error","error":"value error\n"}))
        except serial.SerialException as error:
            self.ws.send(json.dumps({"type":"error","error":"serial exception\n"}))


# def serial_ws_run():
#     # enableTrace(True)
#     ws = SerialWs('ws://localhost:8080/ws', protocols=['http-only', 'chat'])
#     ws.connect()
#     ws.run_forever()


# 各プラットフォームのポートリストを返す
def serial_ports():
    # windowsだったら
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    # linuxだったら
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    # osXだったら
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    # その他はサポート外
    else:
        raise EnvironmentError('Unsupported platform')

    # ポート一覧の表示
    return ports
