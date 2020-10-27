from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.app import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.toolbar import MDToolbar
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import sqlite3
import asyncio
import websockets

kv_code = '''
ScreenManager:
    id: scrn_mngr
    MainWindow:
        id: main_window
    Chat:    
        id: chat
        
<MainWindow>:
    name: 'MainWindow'
    BoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'Anonymous chat'
            MDIconButton:
                icon: './resources/plus.ico'
                text: 'Hello'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: root.manager.current = 'Chat'
        ScrollView:
            MDList:
                padding: 15
                id: chats
        
<Chat>:
    name: 'Chat'
    BoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'chat-name'
            left_action_items: [['arrow-left', lambda x: app.root.ids.chat.go_back()]]
        ScrollView:            
            MDList:
                padding: [0, 15, 15, 15]
                id: messages
'''


class MainWindow(Screen):
    def go_to_chat(self):
        self.parent.current = 'Chat'
        for i in range(4):
            items = TwoLineListItem(text='Name ' + str(i), secondary_text='message')
            self.parent.ids.chat.ids.messages.add_widget(items)
    # def add_chat(self):
    # Добавление чата (создается новая кнопка в поле для перехода на новый Layout


class Chat(Screen):
    def go_back(self):
        self.parent.current = 'MainWindow'
        # self.parent.ids.chat.ids.messages.remove_widget()


class ChatApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainWindow(name='MainWindow'))
        sm.add_widget(Chat(name='Chat'))
        sm = Builder.load_string(kv_code)
        return sm

    def on_start(self):
        for i in range(4):
            items = OneLineListItem(text='Item ' + str(i), on_press=lambda x: self.root.ids.main_window.go_to_chat(),
                                    size_hint=(2, 2))
            self.root.ids.main_window.ids.chats.add_widget(items)


if __name__ == '__main__':
    ChatApp().run()
