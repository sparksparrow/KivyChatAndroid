from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.app import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.button import Button
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
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: chats
                cols: 1
                spacing: 8
                padding: 15
                size_hint_y: None
        
<Chat>:
    name: 'Chat'
    BoxLayout:
        orientation: 'vertical'
        MDToolbar:
            title: 'chat-name'
            left_action_items: [['arrow-left', lambda x: app.root.ids.chat.go_back()]]
        ScrollView:      
            do_scroll_x: False
            do_scroll_y: True      
            MDList:
                padding: [0, 15, 15, 15]
                id: messages
        BoxLayout:
            padding: 5, 0, 5, 0
            size_hint: 1, 0.2
            orientation: 'horizontal'
            cols: 2
            rows: 1
            ScrollView:
                do_scroll_x: False
                do_scroll_y: True
                MDTextField:
                    id: input
                    padding: [15, 15, 15 ,15]
                    max_text_length: 200
                    hint_text: 'Макс. символов: 200'
                    multiline: True
                    mode: 'fill'
                    size_hint: 1, None
                    height: '50dp'
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    required: True
            MDIconButton:
                icon: './resources/send.ico'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: app.root.ids.chat.send_message()
'''


class MainWindow(Screen):
    def go_to_chat(self):
        self.parent.current = 'Chat'
    # def add_chat(self):
    # Добавление чата (создается новая кнопка в поле для перехода на новый Layout


class Chat(Screen):
    def go_back(self):
        self.parent.current = 'MainWindow'

    def send_message(self):
        text_input = self.parent.ids.chat.ids.input.text
        if text_input == '':
            return
        message = TwoLineListItem(text='Me', secondary_text=text_input)
        self.parent.ids.chat.ids.messages.add_widget(message)
        # self.parent.ids.chat.ids.messages.remove_widget()


class ChatApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainWindow(name='MainWindow'))
        sm.add_widget(Chat(name='Chat'))
        sm = Builder.load_string(kv_code)
        return sm

    def on_start(self):
        for i in range(6):
            btn = Button(text='Name ' + str(i), on_press=lambda x: self.root.ids.main_window.go_to_chat(),
                         size_hint_y=None, height=160)
            self.root.ids.main_window.ids.chats.add_widget(btn)


if __name__ == '__main__':
    ChatApp().run()
