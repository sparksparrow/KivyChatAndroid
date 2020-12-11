import asyncio
from datetime import datetime
from collections.abc import Callable
from typing import Dict

from kivymd.uix.list import ThreeLineListItem

try:
    import thread
except ImportError:
    import _thread as thread
import websocket
import json
import time

callbacks: Dict[int, Callable] = {}

# здесь реализованны методы работы по вебсокету
class ClientConnector:
    network_status = False
    db = None
    object_dialog = None
    last_time_connected = None

    def __init__(self, url, port, routes, db): # создает вебсокет подключение с нужными настройками
        self.url, self.port = url, port
        self.routes = routes
        self.db = db
        self.loop = asyncio.get_event_loop()
        self.ws = websocket.WebSocketApp(f"ws://{self.url}:{self.port}",
                                         on_message=self.on_message,
                                         on_open=self.on_open,
                                         on_close=self.on_close
                                         )
        self.connect()

    def on_connected(self, connection): # синхронизирует сообщения
        connection.send('/messages/get',
                        json.dumps({'chat_id': self._id_button[0], 'since': connection.last_time_connected}),
                        callback=lambda _, data: self.get_message_from_server(json.loads(data)))

    def connect(self):
        thread.start_new_thread(self.ws.run_forever, ())

    def on_open(self): # событие вызывается в момент создания вебсокет соединения (даже после потери интернета) и синхронизирует сообщения
        self.network_status = True
        self.on_connected(self)
        self.last_time_connected = None

    def on_close(self): # вызывает в момент потери интернета
        self.network_status = False
        if not self.last_time_connected:
            self.last_time_connected = str(datetime.now()).split('.')[0]
        time.sleep(1)
        self.ws.close()
        self.connect()

    def on_message(self, message): # срабатывает в момент получения сообщения
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

    def send(self, url, message=None, callback=None): # отправляет запрос по вебсокету
        res = {"url": url}
        if message:
            res["data"] = message
        if callback:
            client_id = time.time_ns()
            res['client_id'] = client_id
            callbacks[client_id] = callback
        self.ws.send(json.dumps(res))

    def get_message_from_server(self, response): # получает сообщение и записывает в Ui, выполняет в онлайн режиме пользователя
        for data in response:
            self.db.set_message(text_message=data[0], time=data[1], chat_id=data[3], author=data[2])
            if self.object_chats.parent.current == 'Chat' and self._id_button[0] == data[3]:
                item_mes = ThreeLineListItem(text=data[0], secondary_text=data[2],
                                             tertiary_text=data[1])
                self.object_chats.parent.ids.chat.ids.messages.add_widget(item_mes)

    def set_object_chats(self, object_chats, _id_button):
        self.object_chats = object_chats
        self._id_button = _id_button
