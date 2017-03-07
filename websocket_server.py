from tornado import ioloop, web, websocket
from serial_client import serial_ports
import os, sys, json

class IndexHandler(web.RequestHandler):
    @web.asynchronous
    def get(self):
        ports = serial_ports()
        self.render("index.html", ports=ports)


# websocketハンドラー
class WebSocketHandler(websocket.WebSocketHandler):
    waiters = set()
    # 接続時
    def open(self):
        print(self)
        self.waiters.add(self)
        print("WebSocket opened")

    # 受信時
    def on_message(self, message):
        # 自分以外全てにメッセージ送信
        for waiter in self.waiters:
            if waiter == self:
                continue
            waiter.write_message(message)

    # 切断時
    def on_close(self):
        print(self)
        self.waiters.remove(self)
        print("WebSocket closed")
        for waiter in self.waiters:
            if waiter == self:
                continue
            waiter.write_message(json.dumps({"type":"exit"}))


def ws_server_run():
    # dpath = os.path.dirname(sys.argv[0])
    app = web.Application([
        (r"/", IndexHandler),
        (r"/ws", WebSocketHandler)
    ],
    template_path=os.path.join(os.path.dirname(sys.argv[0]), "templates"),
    # template_path="./templates",
    static_path=os.path.join(os.path.dirname(sys.argv[0]), "static")
    # static_path="./static"
    )
    app.listen(8080)
    ioloop.IOLoop.instance().start()
