import asyncio
from collections.abc import Callable
from typing import Dict

try:
    import thread
except ImportError:
    import _thread as thread
import websocket
import json
import time

callbacks: Dict[int, Callable] = {}


class ClientConnector:

    def __init__(self, url, port, routes):
        self.url, self.port = url, port
        self.routes = routes
        self.last_time_connected = None
        self.loop = asyncio.get_event_loop()
        self.connected = asyncio.Future()
        self.ws = websocket.WebSocketApp(f"ws://{self.url}:{self.port}",
                                         on_message=self.on_message,
                                         on_open=self.on_open,
                                         on_close=self.on_close
                                         )
        self.connect()
        self.loop.run_until_complete(self.connected)

    def on_connected(connection):
        connection.send('/messages/get', json.dumps({'chat_id': 1, 'since': connection.last_time_connected}),
                        callback=lambda _, x: print(x))

    def connect(self):
       # import random
       # print('try', random.randint(0, 10))
        thread.start_new_thread(self.ws.run_forever, ())

    def on_open(self):
        self.loop.call_soon_threadsafe(self.connected.set_result, 0)
        self.on_connected(self)
        self.last_time_connected = None

    def on_close(self):
        if not self.last_time_connected:
            self.last_time_connected = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        time.sleep(1)
        self.ws.close()
        self.connect()

    def on_message(self, message):
        message: Dict = json.loads(message)
        server_id = message.get('server_id')
        client_id = message.get('client_id')
        url = message.get('url')
        if url and server_id:
            handler = self.routes.get(url)
            res = handler(self, message.get('data')) or None
            self.ws.send(json.dumps({"server_id": server_id, "data": res}))
        elif url:
            handler = self.routes.get(url)
            handler(self, message.get('data'))
        elif client_id:
            handler = callbacks.pop(client_id)
            handler(self, message.get('data'))

    def send(self, url, message=None, callback=None):
        res = {"url": url}
        if message:
            res["data"] = message
        if callback:
            client_id = time.time_ns()
            res['client_id'] = client_id
            callbacks[client_id] = callback
        self.ws.send(json.dumps(res))