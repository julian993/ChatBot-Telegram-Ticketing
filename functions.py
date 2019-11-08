import datetime
import threading
import uuid

import requests
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import json
from dbhelper import DBHelper

db = DBHelper()

#gestisce ogni messaggio passato dal main
class Functions:
    TOKEN = "here the key from botfather"
    bot = telepot.Bot(TOKEN)

    headers = {'X-API-Key': 'here the key from osTicket', }#connection with osTicket, get this as apikey
    #on osTicet admin panel

    last_mod = ""
    user = {}#list of registered users
    user_reg = {}
    ticket = {}#list of tickets working on, not finished or sent for review


    #print (ticket[62]['surname'])
    #ticket[62]['creation']='SET'
    #print(ticket[62]['surname'])

    # to remove from dic :del dic[key]
    # to add on dic :dic['item3'] = 3
    user_denied = []#list of denied users, this avoids re-registration after denied
    r = db.get_users()
    for u in r:
        user[u] = 9

    def commands(self, chat, text, user):#non abilitata, possibilita di richiamare funzioni con comandi da telegram
        if text == '/start' and chat not in user:
            return self.deny_user()
        else:
            return False

    def deny_user(self):
        return "Non sei abilitato all'uso di questo ChatBot\nInserisci Nome Cognome Numero di telefono per richiedere l'accesso"

    def deny_user1(self):
        return "Richiesta registrazione già inviata\nAttendi l'esito dell'abilitazione"

    def register(self, chat, text, user_reg):#register a new use
        print(text)
        if self.validate_register(text):
            n, s, num = text.split()
            user_reg[chat] = 0
            return str('Richiesta Registrazione\nUtente {}\nNumero di telefono: {}\nNumero chat: {}'.format(n + ' ' + s,
                                                                                                            str(num),
                                                                                                            str(chat)))
        return False

    def validate_register(self, text):#validate parameters to register new user
        print("v 1", text)
        val = False
        nome, cognome, numero = 0, 0, 0
        try:
            nome, cognome, numero = text.split()
        except ValueError:
            return val
        # print("v 2")
        if nome.isalpha() and cognome.isalpha() and numero.isdigit() and len(numero) == 1:  # Reminder MOD
            val = True
        return val

    def comunicate_admin(self, string, msg):#send to msg the new user registration form
        admin_list = "here id of admin, receiver of the ticket"
        id = "here id of admin, receiver of the ticket"
        # print((admin_list[0]))
        content_type, chat_type, chat_id = telepot.glance(msg)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Approvo', callback_data='approve_user'),
             InlineKeyboardButton(text='NON approvo', callback_data='disapprove_user')],
            # [InlineKeyboardButton(text='Time', callback_data='time')],
        ])
        self.bot.sendMessage(admin_list[0], string, reply_markup=keyboard)

    def send_ticket_admin(self, string):#send to msg the new ticet form
        admin_list = "here id of admin, receiver of the ticket"
        id = "here id of admin, receiver of the ticket"
        # print((admin_list[0]))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Approvo', callback_data='ticket_approve'),#buttons under message, managed by on_callback_query
             InlineKeyboardButton(text='NON approvo', callback_data='ticket_disapprove')],
            # [InlineKeyboardButton(text='Time', callback_data='time')],
        ])
        self.bot.sendMessage(admin_list[0], string, reply_markup=keyboard)

    def start(self, st, user_reg):
        if user_reg:
            string1 = 'Creare nuovo ticket'
            string2 = 'create_new_ticket'
        else:
            string1 = 'Utente Cancellato, richiedi accesso'
            string2 = 'user_denied'
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Vedere i miei ticket', callback_data='view_all_ticket'),
             InlineKeyboardButton(text=string1, callback_data=string2)],
            # [InlineKeyboardButton(text='Time', callback_data='time')],
        ])
        string = "Cosa vuoi fare ?"
        if st == "/start":
            string = "Benvenuto sul chatBot di Topix\n" \
                     "Questo strumento è stato ideato per aiutarti a compilare un ticket e per conoscere lo status di questi\n"+string
        return string, keyboard
        # self.bot.sendMessage(chat_id, "string", reply_markup=keyboard)

    def on_callback_query(self, msg):#manage all the buttons
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', msg['message']['message_id'])

        if query_data == 'approve_user':
            chat_id, nome, cognome, numero = self.split_registration_text(msg['message']['text'])
            string, rp = self.start(chat_id, True)
            self.bot.answerCallbackQuery(query_id, text="Approvato")
            self.bot.sendMessage(chat_id,
                                 "La tua richiesta di registrazione è andata a buon fine"+"\n"+string, reply_markup=rp)
            self.bot.editMessageText(telepot.message_identifier(msg['message']),
                                     msg['message']['text'] + "\nRichiesta Approvata - Utente Registrato")#change original form
            self.input_new_user(chat_id, nome, cognome, self.user_reg)
            # print(msg['message']['text'])
            # prevedere risposta ed inserimento in user db
            # self.comunicate_user("", )
            # my_ip = urlopen('http://ip.42.pl/raw').read()
            # bot.sendMessage(chat_id, my_ip)
        elif query_data == 'disapprove_user':
            chat_id, nome, cognome, numero = self.split_registration_text(msg['message']['text'])
            self.bot.answerCallbackQuery(query_id, text="Disapprovato")
            self.bot.sendMessage(self.split_registration_text(msg['message']['text'])[0],
                                 "La tua richiesta di registrazione NON è andata a buon fine")
            self.bot.editMessageText(telepot.message_identifier(msg['message']),
                                     msg['message']['text'] + "\nRichiesta NON Approvata")
            self.user_denied.append(self.split_registration_text(msg['message']['text'])[0])
            # info = json.dumps(bot.getUpdates(), sort_keys=True, indent=4)
            # bot.sendMessage(chat_id, info)
        elif query_data == 'view_all_ticket':
            self.get_all_ticket(chat_id)
            string, rp = self.start(None, True)
            self.bot.sendMessage(chat_id, string, reply_markup=rp)
        elif query_data == 'create_new_ticket':
            self.input_place(chat_id)
        elif query_data == 'user_denied':
            self.deny_user1()
        elif query_data == 'ticket_approve':
            ticket_id = self.split_ticket_text(msg['message']['text'])
            chat_id = db.get_chat_id_from_id_ticket(ticket_id)
            db.set_status(ticket_id, 8)
            self.bot.sendMessage(chat_id[0], "Approvato\n{} \n{}".format(ticket_id, self.db_ticket_to_string(db.get_ticket_from_id(ticket_id)[0])))
            string, rp = self.start(None, True)
            self.bot.sendMessage(chat_id[0], string, reply_markup=rp)
            self.bot.editMessageText(telepot.message_identifier(msg['message']),
                                     msg['message']['text'] + "\n**Ticket approvato**")
        elif query_data == 'ticket_disapprove':
            ticket_id = self.split_ticket_text(msg['message']['text'])
            chat_id = db.get_chat_id_from_id_ticket(ticket_id)
            db.set_status(ticket_id, 5)
            self.bot.sendMessage(chat_id[0], "NON approvato\n \n{}".format(self.db_ticket_to_string(
                db.get_ticket_from_id(ticket_id)[0])))
            self.bot.editMessageText(telepot.message_identifier(msg['message']),
                                     msg['message']['text'] + "\n**Ticket NON approvato**")


    def comunicate_user(self, string, chat_id):
        self.bot.sendMessage(chat_id, string)

    def get_all_ticket(self, chat):
        result = db.get_ticket(chat, 10)
        if result:
            for ticket in result:
                print(ticket)
                self.bot.sendMessage(chat,
                                     "ID ticket: {}\nNome e Cognome: {} {} \n Con richiesta in data: {} alle ore: {}\n"
                                     " Motivazione: {} Urgenza: {}\n Ingresso con auto: {} Necessità personale ausiliario: {}\n Stato ticket: {}"
                                     .format(ticket[9], ticket[0], ticket[1], ticket[2], ticket[3], ticket[4], ticket[5],
                                             ticket[6], ticket[7], self.ticket_completo(ticket[8])))
        else:
            self.bot.sendMessage(chat, "Non hai ticket")

    def db_ticket_to_string(self, ticket):
        return "ID ticket: {}\nNome e Cognome: {} {} \nCon richiesta in data: {} alle ore: {}\n"\
               "Motivazione: {} Urgenza: {}\n Ingresso con auto: {} Necessità personale ausiliario: {}\n" \
               "Stato ticket: {}".format(ticket[9], ticket[0], ticket[1], ticket[2], ticket[3], ticket[4], ticket[5],
                                         ticket[6], ticket[7], self.ticket_completo(ticket[8]))

    def ticket_completo(self, complete):
        if complete == 8:
            return "approvato"
        elif complete == 5:
            return "NON approvato"
        elif complete == 2:
            return "in attesa di approvazione"
        elif complete == 1:
            return "completo ma non inviato per l'approvazione"
        elif complete == 0:
            return "ticket non completato"
        else:
            return "stato invalido"

    def split_registration_text(self, string):
        mylines = string.splitlines()
        b, nome, cognome = mylines[1].split()
        c, d, e, numero = mylines[2].split()
        a, chat_id = mylines[3].split(": ")
        return chat_id, nome, cognome, numero
    # return tutti i campi
    def split_ticket_text(self, string):
        mylines = string.splitlines()
        b, id = mylines[0].split(": ")
        return id

    def input_new_user(self, chat, nome, cognome, user_reg):
        db.register_user(chat, nome, cognome)
        r = db.get_users()
        for u in r:
            self.user[u] = 9
        # user_reg.remove(chat)
        # db.set_last_step(chat, 8)

    def batch(self):
        threading.Timer(2.0, self.batch).start()  # set time,linked to refresh rate
        self.user.clear()
        r = db.get_users()
        for u in r:
            self.user[u] = 9
            # self.user[u] = {'ticket':9, 'place':'null', 'urgency':'null', 'date':'null', 'time':'null', 'purpose':'null'
            #    , 'car':'null', 'support':'null', 'name':'null', 'surname':'null', 'creation':'null'}
        # self.user[u]['place'] = 'AAAAAAAAAAA'
        #print(self.user)
        #print(self.ticket)

    def check_reg(self, chat_id, user_reg):
        if chat_id in user_reg:
            return True
        return False

    def input_place(self, chat):
        #self.ticket[chat]['state'] = 1
        #get here id ticket from osTicket
        self.ticket[chat] = {'id' : str(uuid.uuid4().fields[-1])[:5], 'state': 1, 'place': 'null', 'urgency': 'ordinaria', 'date': 'null', 'time': 'null',
                      'purpose': 'manutenzione'
            , 'car': 'no', 'support': 'no', 'name': 'null', 'surname': 'null', 'creation': 'null'}
        #db.set_last_step(chat, 6)
        #place = db.get_trend(chat)
        keyboard = ReplyKeyboardMarkup(keyboard=[['Alessandria', 'Ivrea'], ['Novara', 'Milano']], one_time_keyboard = True)
        self.bot.sendMessage(chat, "Inserisci il luogo in cui vuoi un intervento (per ora solo a ed alessandria)",
                             reply_markup=keyboard)

    def check_input_place(self, chat, text):
        # 1
        # print("check_input_place", db.get_ticket_status(chat)[0])
        #verifica posto in db cambiare
        self.ticket[chat]['place'] = text
        return self.input_urgency(chat)

    def input_urgency(self, chat):
        keyboard = ReplyKeyboardMarkup(keyboard=[['ordinaria', 'straordinaria']], one_time_keyboard = True)
        self.ticket[chat]['state']=2
        return "Seleziona l'urgenza dell'intervento", keyboard

    def check_input_urgency(self, step, chat, text):
        #2
        if text != "ordinaria" and text != "straordinaria" and not text.startswith('o') and not text.startswith('s'):
            urgenza = {"ordinaria", "straordinaria"}
            keyboard = ReplyKeyboardMarkup(keyboard=[['ordinaria', 'straordinaria']], one_time_keyboard = True)
            return "Urgenza specificata non corretta, specificare se ordinaria o straordinaria ", keyboard
        else:
            if text.startswith('o'):
                text = 'ordinaria'
            if text.startswith('s'):
                text = 'straordinaria'
            self.ticket[chat]['urgency'] = text
            return self.input_date(step, chat)

    def input_date(self, step, chat):
        urgenza = [(datetime.date.today() + datetime.timedelta(days=1)).strftime('%d-%m-%Y'),
                   (datetime.date.today() + datetime.timedelta(days=2)).strftime('%d-%m-%Y'),
                   (datetime.date.today() + datetime.timedelta(days=3)).strftime('%d-%m-%Y'),
                   (datetime.date.today() + datetime.timedelta(days=4)).strftime('%d-%m-%Y')]
        keyboard = ReplyKeyboardMarkup(keyboard=[[urgenza[0], urgenza[1]], [urgenza[2], urgenza[3]]], one_time_keyboard = True)
        self.ticket[chat]['state'] = 3
        return "Specificare data tramite le opzioni sottostanti altrimenti in formato gg-mm-yyyy", keyboard

    def check_input_date(self, step, chat, text):
        # 3
        if self.validate(text):
            self.ticket[chat]['date'] = text
            return self.finish_ticket(self.ticket, chat)#intermezzo
        else:
            return self.input_date(step, chat)

    def validate(self, date_text):
        # print("validate", date_text)
        val = True
        day, month, year = 0, 0, 0  # DAFARE mancano controlli di date plausibili con range
        try:
            day, month, year = date_text.split('-')
        except ValueError:
            val = False
        try:
            datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            val = False
        # print("val", val)
        return val

    def finish_ticket(self, ticket, chat):
        self.ticket[chat]['state'] = 4
        self.ticket[chat]['name'] = db.get_name(chat)[0]
        self.ticket[chat]['surname'] = db.get_surname(chat)[0]
        string = self.ticket_to_string(ticket, chat)
        keyboard = ReplyKeyboardMarkup(keyboard=[['SI', 'NO']], one_time_keyboard = True)
        return string+"\n\nVuoi confermare questo ticket ?", keyboard

    #def end(self, chat):
    #    db.create_ticket(chat, self.ticket)
    #    self.send_ticket_admin(chat)
    #    return "Ticket FINITO, manca ancora il review del ticket e il conferma ticket per l'invio dell'esito", None

    def ticket_to_string(self, ticket, chat):
        return "ID ticket: {}\nNome e Cognome: {} {} \nCon richiesta in data: {} alle ore: {}\nMotivazione: {} Urgenza: {}\nIngresso con auto: {} Necessità personale ausiliario: {}\nStato ticket: {}".format(
            ticket[chat]['id'], ticket[chat]['name'], ticket[chat]['surname'], ticket[chat]['date'],
            ticket[chat]['time'], ticket[chat]['purpose'], ticket[chat]['urgency'], ticket[chat]['car'],
            ticket[chat]['support'], ticket[chat]['state'])

    def check_finish_ticket(self, chat, text):
        #4
        if text == "SI" or text == "si" or text == "Si":
            self.ticket[chat]['state'] = 10
            db.create_ticket(chat, self.ticket)
            self.send_ticket_admin(self.ticket_to_string(self.ticket, chat))
            data = {
                "name": self.ticket[chat]['name'],
                "email": "test@gmail.com",
                "subject": "MSG FROM CHATBOT",
                "message": self.ticket_to_string(self.ticket, chat),
                "priority": self.define_priority(self.ticket[chat]['urgency']),
                "topicId": "1",
                "source_extra": self.ticket[chat]['id'],
            }
            data1 = json.dumps(data)
            response = requests.post('http://localhost/OS/api/tickets.json', data=data1, headers=self.headers)
            print(response.text)
            #add retrieve of id ticket
        elif text == 'NO' or text == 'no' or text == 'No':
            del self.ticket[chat]
            #db.remove_ticket(self.ticket[chat]['id'])
        else:
            self.finish_ticket(self.ticket, chat)
        string, rp = self.start(None, True)
        string = "Ticket inviato per la verifica, attendi esito\n"+string
        return string, rp

    def define_priority(self, urg):
        if urg == "ordinaria":
            return 2
        else:
            return 3


    #def get_user_info(self):
    #    return self.user[]

    #def post_ticket(json):
    #    headers = {'API-Key': 'mykey'}
    #    response = requests.post("http://localhost/upload/api/tickets.json", data=create_json_ticket(json), headers=headers)
    #    for r in response:
    #        print(r)