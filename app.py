from websocket_server import ws_server_run
from serial_client import SerialWs
import time, subprocess, os, sys, threading

if __name__ == '__main__':
    serial_thread = threading.Thread(target=ws_server_run)
    serial_thread.setDaemon(True)
    serial_thread.start()

    time.sleep(0.5)

    # subprocess.call('open -a ' + os.path.join(os.path.dirname(sys.argv[0]), "SerialTool.app"),shell=True)

    ws = SerialWs('ws://localhost:8080/ws', protocols=['http-only', 'chat'])
    ws.connect()
    ws.run_forever()
