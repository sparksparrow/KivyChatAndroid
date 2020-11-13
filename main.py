from kivy.app import Builder
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.button import Button as MDButton
from datetime import datetime
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import ObjectProperty
from DB import DBController
import asyncio
import websockets

kv_code = '''
ScreenManager:
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
                size_hint: 1, None
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
                icon_right: 'account'
                mode: 'rectangle'
                on_focus: root.save_username()
            Widget:
            
<Chat>:
    name: 'Chat'
    BoxLayout:
        id: box_chat
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
            size_hint: 1, 0.3
            orientation: 'horizontal'
            cols: 2
            rows: 1    
            Widget:
                size_hint: 0.04, 1          
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
                on_focus: root.ui_keyboard()
            Widget:   
                size_hint: 0.01, 1 
            MDIconButton:
                icon: 'arrow-up-circle'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: root.send_message()               
'''

db = DBController()
id_instance_button = dict()
id_button = int()


class ScreenController(ScreenManager):
    class MainWindow(MDScreen):
        dialog = None

        def on_kv_post(self, base_widget):
            self.parent.ids.main_window.ids.input_username.text = db.get_username()

        def go_to_chat(self, instance):
            if self.parent.ids.main_window.ids.input_username.text != '':
                for key, value in id_instance_button.items():
                    if instance is value:
                        global id_button
                        id_button = key
                print(id_button)
                self.parent.transition.direction = 'left'
                self.parent.current = 'Chat'
            else:
                if not self.dialog:
                    self.dialog = MDDialog(text='Enter your username')
                self.dialog.open()

        def save_username(self):
            db.set_username(self.parent.ids.main_window.ids.input_username.text)
        # def add_chat(self):
        # Добавление чата (создается новая кнопка в поле для перехода на новый Layout

    class Chat(MDScreen):
        keyboard = None

        def on_pre_enter(self, *args):
            global id_button
            messages = db.get_messages(id_button)
            for message in messages:
                item_mes = ThreeLineListItem(text=message[0], secondary_text=message[2], tertiary_text=message[1])
                self.parent.ids.chat.ids.messages.add_widget(item_mes)

        def go_back(self):
            self.parent.transition.direction = 'right'
            self.parent.current = 'MainWindow'

        def send_message(self):
            text_input = self.parent.ids.chat.ids.input.text
            date_sent = str(datetime.now())[:-7]
            if text_input == '':
                return
            db.set_message(text_input, date_sent, 1)
            item_mes = ThreeLineListItem(text=text_input, secondary_text=db.get_username(),
                                         tertiary_text=date_sent)
            self.parent.ids.chat.ids.messages.add_widget(item_mes)
            self.parent.ids.chat.ids.input.text = ''

        def ui_keyboard(self):
            if not self.keyboard:
                self.keyboard = Widget(size_hint=(None, 1.3))
                self.parent.ids.chat.ids.box_chat.add_widget(self.keyboard)
            else:
                self.parent.ids.chat.ids.box_chat.remove_widget(self.keyboard)
                self.keyboard = None

        def on_pre_leave(self, *args):
            self.parent.ids.chat.ids.messages.clear_widgets()


sm = ScreenController()


class ChatApp(MDApp):

    def build(self):
        screen = Builder.load_string(kv_code)
        return screen

    def on_start(self):
        chats = db.get_chats()
        for chat in chats:
            btn = MDButton(text=chat[1], font_size=50, on_press=lambda x: self.root.ids.main_window.go_to_chat(x),
                           size_hint_y=None, height=160)
            id_instance_button[chat[0]] = btn
            self.root.ids.main_window.ids.chats.add_widget(btn)

    def on_stop(self):
        db.close_con()


if __name__ == '__main__':
    ChatApp().run()
