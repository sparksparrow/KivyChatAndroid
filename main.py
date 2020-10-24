from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.app import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import sqlite3
import asyncio
import websockets

Builder.load_string('''
<MainWindow>:
    rows: 3


    AnchorLayout:
        size_hint: 1, 0.10

        BoxLayout:
            cols: 2
            orientation: 'horizontal'
            Label:
                font_name: './resources/appetite.ttf'
                markup: True
                text: 'Anonymous chat'
                font_size: '35px'
                canvas.before:
                    Color:
                        rgba: 0.5, 0.5, 1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.parent.size
                valign: 'middle'
                text_size: self.size
            Button:
                id: add_chat
                size_hint: 0.2, 1
                background_color: 0.1, 0.1, 0.1, 0.2
                on_release: root.add_chat()
                Image:
                    allow_stretch: True
                    size: self.parent.size
                    pos: self.parent.pos
                    source: './resources/add.png'

    AnchorLayout:
        padding: [15, 15, 15, 0]
        cols:1
        BoxLayout:
            orientation: 'vertical'
            Button:
                size_hint: 1, 0.2
                background_color: 0.5, 0.5, 1, 1
            Button:
                size_hint: 1, 0.2
                background_color: 0.5, 0.5, 1, 1

    AnchorLayout:
        size_hint: 1,0.15
''')


class MainWindow(GridLayout):

    def add_chat(self):
        pass  # Добавление чата (создается новая кнопка в поле для перехода на новый Layout


class ChatApp(App):
    def build(self):
        return MainWindow()



if __name__ == '__main__':
    ChatApp().run()
