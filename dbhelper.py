import datetime
import time
import sqlite3
import uuid


class DBHelper:

    def __init__(self, dbname = "/Users/julian/Documents/ChatBot/datab.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)#False bc of multi-threading access on every msg


    def setup(self):
        print("SETUP")
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.commit()

    def add_item(self, item_text, owner):
        stmt = "INSERT INTO items (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, owner):
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_questions(self, q):
        #print("domanda 1 - " + q)
        stmt = "SELECT a FROM keywords WHERE q LIKE (?)"
        args = (q,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_answers(self, q):
        stmt = "SELECT answer.answer FROM answer JOIN keyword ON answer.id_a=keyword.id_a WHERE keyword.q = (?)"
        args = (q,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def exist_quest(self, q):
        stmt = "SELECT q FROM keyword WHERE q = (?)"
        args = (q,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def write_ticket(self, campo, owner):
        stmt = "INSERT INTO ticket (description, owner) VALUES (?, ?)"
        args = (campo, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def exist_user(self, chat_id):
        stmt = "SELECT name FROM user WHERE chat_id = (?)"
        args = (chat_id,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def register_user(self, chat_id, nome, cognome):
        stmt = "INSERT INTO user (chat_id, name, surname) VALUES (?, ?, ?)"
        args = (chat_id, nome, cognome)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_last_step(self, chat):
        stmt = "SELECT last_step FROM user WHERE chat_id = (?)"
        args = (chat,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def dec_last_step(self, chat_id):
        stmt = "UPDATE user SET last_step = last_step-1 WHERE chat_id=(?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def inc_last_step(self, chat_id):
        stmt = "UPDATE user SET last_step = last_step+1 WHERE chat_id=(?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def inc_complete(self, chat_id):
        stmt = "UPDATE ticket SET status = status + 1 WHERE chat_id=(?) and status <= 1"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def exist_place(self, text):
        stmt = "SELECT place.name FROM place WHERE name LIKE (?)"
        args = (text,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_name(self, chat_id):
        stmt = "SELECT name FROM user WHERE chat_id = (?)"
        args = (chat_id,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def set_name(self, chat_id, name, surname):
        stmt = "UPDATE user SET name = (?), surname = (?) WHERE chat_id=(?)"
        args = (name, surname, chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_surname(self, chat_id):
        stmt = "SELECT surname FROM user WHERE chat_id = (?)"
        args = (chat_id,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def create_ticket(self, chat_id, ticket):
        #print("create_ticket")
        dt = datetime.datetime.now()
        ticket[chat_id]['name'] = self.get_name(chat_id)[0]
        ticket[chat_id]['surname'] = self.get_surname(chat_id)[0]
        cod = ticket[chat_id]['id']
        stmt = "INSERT INTO ticket (chat_id, name, surname, creation, id, urgency, place, date, time, purpose, car, support, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2)"
        args = (chat_id, ticket[chat_id]['name'], ticket[chat_id]['surname'], (datetime.datetime.now()).replace(second=0, microsecond=0), cod,
                ticket[chat_id]['urgency'], ticket[chat_id]['place'], ticket[chat_id]['date'],
                ticket[chat_id]['time'], ticket[chat_id]['purpose'], ticket[chat_id]['car'], ticket[chat_id]['support'])
        self.conn.execute(stmt, args)
        self.conn.commit()

    def remove_ticket(self, ticket_id):
        stmt = "DELETE FROM ticket WHERE id = (?)"
        args = (ticket_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def exist_ticket(self, chat_id):
        stmt = "SELECT chat_id FROM ticket WHERE chat_id = (?) AND status < 2"
        args = (chat_id,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def p_exist_ticket(self, id):
        stmt = "SELECT name FROM ticket WHERE id = (?)"
        args = (id,)
        return [x[0] for x in self.conn.execute(stmt, args)]


    def insert_ticket(self, step, chat_id, text):
        campo = 'place'
        print("DB step", step)
        if step == 6:
            campo = 'place'
        elif step == 5:
            campo = 'urgency'
        elif step == 4:
            campo = 'date'
        elif step == 3:
            campo = 'time'
        elif step == 11:
            campo = 'purpose'
        elif step == 12:
            campo = 'car'
        #print(("campo " + campo))
        #print(("campo " + campo))
        stmt = "UPDATE ticket SET " + campo + " = (?) WHERE chat_id = (?) AND status <= 1"
        args = (text, chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()
        if campo == 'place':
            self.set_trend(chat_id, text)

    def reset(self, chat_id):
        if self.exist_ticket(chat_id):
            stmt = "DELETE FROM ticket WHERE chat_id = (?) AND status < 2"
            args = (chat_id,)
            self.conn.execute(stmt, args)
            self.conn.commit()
        stmt = "UPDATE user SET last_step = 7 WHERE chat_id = (?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_trend(self, chat_id):
        stmt = "SELECT trend FROM user WHERE chat_id = (?)"
        args = (chat_id,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def set_trend(self, chat_id, trend):
        stmt = "UPDATE user SET trend = (?) WHERE chat_id = (?)"
        args = (trend, chat_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_ticket(self, chat_id, complete):
        stmt = "SELECT name, surname, date, time, purpose, urgency, car, support, status, id  FROM ticket WHERE chat_id = (?) AND status <= (?) ORDER BY date, time"
        args = (chat_id, complete, )
        return [x for x in self.conn.execute(stmt, args)]

    def p_get_ticket(self, complete):
        stmt = "SELECT name, surname, date, time, purpose, urgency, car, support, status, id  FROM ticket WHERE status <= (?)"
        args = (complete, )
        return [x for x in self.conn.execute(stmt, args)]

    def set_last_step(self, chat, step):
        stmt = "UPDATE user SET last_step = (?) WHERE chat_id = (?)"
        args = (step, chat)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_ticket_status(self, chat):
        stmt = "SELECT status FROM ticket WHERE chat_id = (?) AND status < 2"
        args = (chat, )
        return [x[0] for x in self.conn.execute(stmt, args)]


    def check_status_ticket(self, chat, stato):
        stmt = "SELECT status FROM ticket WHERE chat_id = (?) AND status = (?)"
        args = (chat, stato, )
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_ticket_from_id(self, id):
        stmt = "SELECT name, surname, date, time, purpose, urgency, car, support, status, id FROM ticket WHERE id = (?) LIMIT 1"
        args = (id,)
        return [x for x in self.conn.execute(stmt, args)]

    def p_get_ticket_from_id(self, id):
        stmt = "SELECT name, surname, date, time, purpose, urgency, car, support, status, id FROM ticket WHERE id = (?) LIMIT 1"
        args = (id, )
        return [x for x in self.conn.execute(stmt, args)]

    def get_priv(self, chat):
        stmt = "SELECT top FROM user WHERE chat_id = (?)"
        args = (chat, )
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_admin(self):
        stmt = "SELECT chat_id FROM user WHERE top = 1"
        args = ()
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_users(self):
        stmt = "SELECT chat_id, top FROM user"
        args = ()
        return [x[0] for x in self.conn.execute(stmt, args)]

    def set_status(self, id, d):
        stmt = "UPDATE ticket SET status = (?) WHERE id = (?)"
        args = (d, id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def mod(self, tab, last_mod):#refresh every last_update <>
        stmt = "SELECT Timestamp FROM time_stamp WHERE table_type LIKE (?)"
        args = (tab,)
        return [last_mod == (x[0] for x in self.conn.execute(stmt, args))]

    def get_chat_id_from_id_ticket(self, id):
        stmt = "SELECT chat_id top FROM ticket where id = (?)"
        args = (id,)
        return [x[0] for x in self.conn.execute(stmt, args)]
