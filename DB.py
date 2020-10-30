import sqlite3


class DBController():
    con = None
    cur = None
    path_db = './Chats_base.db'
    table_chat = ('''
                    CREATE TABLE IF NOT EXISTS chat( id INTEGER PRIMARY KEY, 
                                                     chat_name TEXT NOT NULL)
                 ''')
    table_message = ('''
                    CREATE TABLE IF NOT EXISTS message( id INTEGER PRIMARY KEY,
                                                        text_message TEXT NOT NULL, 
                                                        time TEXT NOT NULL, 
                                                        author TEXT NOT NULL, 
                                                        chat_id INTEGER NOT NULL, 
                                                        FOREIGN KEY (chat_id) REFERENCES chat(id))
                    ''')

    query_select_chats = ('''
                            SELECT *
                            FROM chat
                            ''')

    query_select_messages = ('''
                            SELECT text_message,time,author
                            FROM message
                            WHERE chat_id = 
                             ''')

    def __init__(self):
        try:
            self.con = sqlite3.connect(self.path_db)
            self.cur = self.con.cursor()
            self.cur.execute(self.table_chat)
            self.cur.execute(self.table_message)
        except ConnectionError:
            return

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
            self.cur.execute(self.query_select_messages+str(id))
            messages = self.cur.fetchall()
            self.cur.close()
            self.cur = self.con.cursor()
            return messages
        except BaseException:
            return list()

    @staticmethod
    def close_con(self):
        self.cur.close()
        self.con.close()
