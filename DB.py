import sqlite3
from string import Template

# Это должен был быть статический класс, но здесь нельзя создавать статические поля, только методы:(
class DBController:
    con = None
    cur = None
    path_db = './Chats_base.db'
    table_chat = '''CREATE TABLE IF NOT EXISTS chat( id INTEGER PRIMARY KEY, 
                                                     chat_name TEXT NOT NULL)'''

    table_message = '''CREATE TABLE IF NOT EXISTS message( id INTEGER PRIMARY KEY,
                                                        text_message TEXT NOT NULL, 
                                                        time TEXT NOT NULL, 
                                                        author TEXT NOT NULL, 
                                                        chat_id INTEGER NOT NULL, 
                                                        FOREIGN KEY (chat_id) REFERENCES chat(id))'''

    table_username = '''CREATE TABLE IF NOT EXISTS options( key TEXT PRIMARY KEY,
                                                            value TEXT);'''

    query_select_chats = '''SELECT *
                            FROM chat'''

    query_select_messages = '''SELECT text_message,time,author
                            FROM message
                            WHERE chat_id = '''

    query_insert_username = '''INSERT INTO options VALUES('username','Guest')'''

    query_select_username = '''SELECT value FROM options WHERE key='username' '''

    query_update_username = Template('''UPDATE options SET value='$new_value' WHERE key='username' ''')

    def __init__(self):
        try:
            self.con = sqlite3.connect(self.path_db)
            self.cur = self.con.cursor()
            self.cur.execute(self.table_chat)
            self.cur.execute(self.table_message)
            self.cur.execute(self.table_username)
            self.init_username(self)
            self.con.commit()
        except ConnectionError:
            return

    @staticmethod
    def init_username(self):
        if not self.cur.execute(self.query_select_username).fetchall():
            self.cur.execute(self.query_insert_username)

    @staticmethod
    def get_chats(self):
        try:
            self.cur.execute(self.query_select_chats)
            chats = self.cur.fetchall()
            self.cur.close()
            self.cur = self.con.cursor()
            return chats
        except BaseException:
            return list()

    @staticmethod
    def get_messages(self, id):
        try:
            self.cur.execute(self.query_select_messages + str(id))
            messages = self.cur.fetchall()
            self.cur.close()
            self.cur = self.con.cursor()
            return messages
        except BaseException:
            return list()

    def set_message(self):
        pass

    @staticmethod
    def get_username(self):
        try:
            self.cur.execute(self.query_select_username)
            username = self.cur.fetchone()[0]
            self.cur.close()
            self.cur = self.con.cursor()
            return username
        except BaseException:
            return str()

    @staticmethod
    def set_username(self, new_username):
        try:
            self.cur.execute(self.query_update_username.substitute(new_value=new_username))
            self.con.commit()
            self.cur.close()
            self.cur = self.con.cursor()
            return
        except BaseException:
            return

    @staticmethod
    def close_con(self):
        self.cur.close()
        self.con.close()
