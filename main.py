from kivy.app import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.button import Button as MDButton
from datetime import datetime
from kivymd.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from DB import DBController
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
                icon: 'settings'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: nav_drawer.toggle_nav_drawer()
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: chats
                cols: 1
                spacing: 8
                padding: 15
                size_hint_y: None
    MDNavigationDrawer:
        id: nav_drawer
        BoxLayout:
            padding: [15, 15, 50 ,15]
            orientation: 'vertical'
            MDTextField:
                id: input_username
                multiline: False
                mode: 'line'
                max_text_length: 30
                hint_text: 'Username     '
                icon_right: 'account'
                mode: 'rectangle'
                on_focus: root.save_username()
            Widget:
            
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
                id: messages
                padding: [0, 15, 15, 15] 
        BoxLayout:
            padding: 10, 0, 5, 0
            size_hint: 1, 0.2
            orientation: 'horizontal'
            cols: 2
            rows: 1            
            MDTextField:
                id: input
                padding: [15, 15, 15 ,15]
                max_text_length: 5000
                mode: 'rectangle'
                multiline: False
                size_hint: 1, None
                height: '50dp'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_text_validate: root.send_message()
            MDIconButton:
                icon: 'arrow-up-circle'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: root.send_message()               
'''

db = DBController()


class MainWindow(Screen):
    username = str()

    def go_to_chat(self):
        self.parent.current = 'Chat'

    def save_username(self):
        self.username = self.parent.ids.main_window.ids.input_username.text
    # def add_chat(self):
    # Добавление чата (создается новая кнопка в поле для перехода на новый Layout


class Chat(Screen):
    list_messages = list()

    def on_pre_enter(self, *args):
        messages = db.get_messages(db, 1)
        for message in messages:
            item_mes = ThreeLineListItem(text=message[0], secondary_text=message[2], tertiary_text=message[1])
            self.parent.ids.chat.ids.messages.add_widget(item_mes)
            self.list_messages.append(item_mes)

    def go_back(self):
        self.parent.current = 'MainWindow'

    def send_message(self):
        text_input = self.parent.ids.chat.ids.input.text
        if text_input == '':
            return
        item_mes = ThreeLineListItem(text=text_input, secondary_text='Me', tertiary_text=str(datetime.now())[:-7])
        self.parent.ids.chat.ids.messages.add_widget(item_mes)
        self.list_messages.append(item_mes)
        self.parent.ids.chat.ids.input.text = ''

    def on_pre_leave(self, *args):
        for i in range(len(self.list_messages)):
            self.parent.ids.chat.ids.messages.remove_widget(self.list_messages[i])
        self.list_messages = list()


class ChatApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainWindow(name='MainWindow'))
        sm.add_widget(Chat(name='Chat'))
        sm = Builder.load_string(kv_code)
        return sm

    def on_start(self):
        chats = db.get_chats(db)
        for chat in chats:
            btn = MDButton(text=chat[1], on_press=lambda x: self.root.ids.main_window.go_to_chat(),
                           size_hint_y=None, height=160)
            self.root.ids.main_window.ids.chats.add_widget(btn)

    def on_stop(self):
        db.close_con(db)


if __name__ == '__main__':
    ChatApp().run()
