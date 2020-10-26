from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.app import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.toolbar import MDToolbar
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import sqlite3
import asyncio
import websockets

kv_code = '''
ScreenManager:
    MainWindow:
    Chat:    
        
<MainWindow>:
    name: 'MainWindow'
    BoxLayout:
        orientation: "vertical"
        MDToolbar:
            title: 'Anonymous chat'
            MDIconButton:
                icon: './resources/plus.ico'
                text: 'Hello'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: root.manager.current = 'Chat'
        ScrollView:
            MDList:
                id: container
                OneLineListItem:
                    text: 'Item1'
                OneLineListItem:
                    text: 'Item2'
        
<Chat>:
    name: 'Chat'
    MDRectangleFlatButton:
        text: 'Hello'
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        on_press: root.manager.current = 'MainWindow'

'''


class MainWindow(Screen):
    # def add_chat(self):
    pass  # Добавление чата (создается новая кнопка в поле для перехода на новый Layout


class Chat(Screen):
    pass


sm = ScreenManager()
sm.add_widget(MainWindow(name='MainWindow'))
sm.add_widget(Chat(name='Chat'))


class ChatApp(MDApp):
    def build(self):
        sm = Builder.load_string(kv_code)
        return sm

    # def on_start(self):
    #     for i in range(4):
    #         items = OneLineListItem(text='Item '+str(i))
    #         MainWindow.get_root_window(self).ids.container.add_widget(items)


if __name__ == '__main__':
    ChatApp().run()
