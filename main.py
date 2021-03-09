from kivy.app import Builder
from kivymd.theming import ThemeManager
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.button import Button as MDButton
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from db_controller import DBController
from ws_controller import WSConstroller
from kivy.core.window import Window

try:
    import thread
except ImportError:
    import _thread as thread

Window.size = (540, 960)
# kv-код, отрисовывающий ui приложения, что-то типо kivy front-end
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
            id: toolbar_name
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
            Widget:   
                size_hint: 0.01, 1 
            MDIconButton:
                icon: 'arrow-up-circle'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                on_press: root.send_message()               
'''

db = DBController() # создание класа для работы с бд
_id_instance_button = dict() # хранит id кнопок и их объект
_id_button = [0] # хранит id активной кнопки (по той что перешли в чат)
ws = WSConstroller(db=db) # создает класс для работы в вебсокетами
theme_cls = ThemeManager() # менеджер тем, хранит цвета и разметку

# класс управления всеми экранами (Layout'ами)
class ScreenController(ScreenManager):
    # главный экран (Layout), экран чатов
    class MainWindow(MDScreen):
        dialog = None

        def on_kv_post(self, base_widget): # выполняет в момент парсинга kv-кода (kivy front-end)
            thread.start_new_thread(lambda: ws.synch_all(self, [_id_button, theme_cls]), ())
            self.parent.ids.main_window.ids.input_username.text = db.get_username()

        def go_to_chat(self, instance, ref_id_button): # переход в окно диалога выбранного чата
            local_id_instance_button = _id_instance_button
            if ws.get_id_instance_buttons():
                local_id_instance_button = ws.get_id_instance_buttons()
            if self.parent.ids.main_window.ids.input_username.text != '':
                for key, value in local_id_instance_button.items():
                    if instance == value:
                        ref_id_button[0] = key
                self.parent.transition.direction = 'left'
                self.parent.current = 'Chat'
            else:
                if not self.dialog:
                    self.dialog = MDDialog(text='Enter your username')
                self.dialog.open()

        def save_username(self): # записывает имя пользователя
            db.set_username(self.parent.ids.main_window.ids.input_username.text)

    # экран диалога чата (Layout)
    class Chat(MDScreen):
        keyboard = None

        # срабатывает в момент перехода на экран, рисует диалог
        def on_pre_enter(self, *args):
            self.parent.ids.chat.ids.toolbar_name.title = db.get_chat_name(_id_button[0])
            ws.set_id_button(_id_button)
            Window.bind(on_key_down=self.key_action)
            messages = db.get_messages(_id_button[0])
            for message in messages:
                item_mes = ThreeLineListItem(text=message[0], secondary_text=message[2], tertiary_text=message[1])
                self.parent.ids.chat.ids.messages.add_widget(item_mes)
            ws.synch_messages()

        # возвращается на главный экран
        def go_back(self):
            self.parent.transition.direction = 'right'
            self.parent.current = 'MainWindow'

        # отправка сообщения
        def send_message(self):
            text_input = self.parent.ids.chat.ids.input.text
            date_sent = str(datetime.now())[:-7]
            username = db.get_username()
            if text_input == '':
                return
            ws.send_message(text_input, date_sent, username, _id_button[0], self)
            self.parent.ids.chat.ids.input.text = ''

        # обработка кнопки "BACK" на android
        def key_action(self, *args):
            if args[1] == 27 and self.parent.current == 'Chat':
                self.go_back()
                return True
            elif args[1] == 27 and self.parent.current == 'MainWindow':
                MDApp.get_running_app().stop()
                return True
            return
        # срабатывает в момент выхода из диалога, очищает диалог
        def on_pre_leave(self, *args):
            self.parent.ids.chat.ids.messages.clear_widgets()


screen_manager = ScreenController() # объявляет класс управления экранами


class ChatApp(MDApp):

    # строит приложение по kv-коду
    def build(self):
        screen = Builder.load_string(kv_code)
        return screen

    # вызываеься после создания kv-кода, рисует ui, на момент пока нет интернета
    def on_start(self):
        ws.set_object_chats(self.root.ids.chat, _id_button)
        Window.softinput_mode = 'below_target'
        chats = db.get_chats()
        for chat in chats:
            btn = MDButton(text=chat[1], font_size=50, bold=True,
                           on_press=lambda x: self.root.ids.main_window.go_to_chat(instance=x,
                                                                                   ref_id_button=_id_button),
                           size_hint_y=None, height=theme_cls.standard_increment * 1.5,
                           background_color=(0, 0.749, 1, 0.5))
            _id_instance_button[chat[0]] = btn
            self.root.ids.main_window.ids.chats.add_widget(btn)


if __name__ == '__main__':
    ChatApp().run()
