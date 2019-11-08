import telepot #library mostly for sending/getting messages
from telepot.loop import MessageLoop
from functions import Functions
f=Functions()
from dbhelper import DBHelper
db = DBHelper()
import time

class Main:
    TOKEN = "here token ftom chatbot"#get this from @botFather
    db.setup()#create db conn
    def on_chat_message(self):
        print("ciao")
        content_type, chat_type, chat_id = telepot.glance(self)
        #print("ciao", msg['text'])
        c_user = False
        if chat_id in f.user.keys():
            c_user = True
        text = self['text']
        print("c_user", c_user)
        if chat_id in f.ticket.keys():
            workingTicket = True
        else:
            workingTicket = False
        # prevedere due tipi di user, uno admin e uno client
        # quests=db.exist_quest(chat)
        # items = db.get_items(chat)  ##
        last_step = 10  # gestire caso senza utente registrato
        print("user -", chat_id)
        string = "NULL"
        rp=None
        print(f.user)
        if c_user:#check in user is registered
            #last_step = int(f.user[chat_id])
            if chat_id in f.ticket.keys():#if user is creating a ticket
                if f.ticket[chat_id]['state'] == 1:
                    string, rp = f.check_input_place(chat_id, text)
                elif f.ticket[chat_id]['state'] == 2:
                    string, rp = f.check_input_urgency(2, chat_id, text)
                elif f.ticket[chat_id]['state'] == 3:
                    string, rp = f.check_input_date(3, chat_id, text)
                elif f.ticket[chat_id]['state'] == 4:
                    string, rp = f.check_finish_ticket(chat_id, text)
                else:
                    string, rp = f.start(None, c_user)
            else:
            #f.choose_case(last_step, chat_id, "text")
                string, rp = f.start(text, c_user)
        else:
            if chat_id in f.user_reg and chat_id not in f.user_denied:
                string = f.deny_user1()
            else:
                if chat_id in f.user_denied:
                    string = "ACCESSO NEGATO\nCi spiace ma la tu richiesta non è stata accettata, per eventuali " \
                             "informazione sul motivo contattaci via mail -------- "
                else:
                    register = f.register(chat_id, text, f.user_reg)
                    #print(register)
                    if not register and text == '/start':
                        string = "Benvenuto al chatBot di support TOP-IX\nQuesto chatBot ti guiderà nella creazione del tuo ticket per richiedere l'accesso ai vari datacenter\nAl momento risulti un utente non registrato per cui non autorizzato\nPer richiedere l'accesso rispondi con: Nome(spazio)Cognome(spazio)Numero di telefono [UNA SOLA CIFRA]"
                    elif not register and text != '/start':
                        string = 'Non hai inserito i parametri in maniera corretta: Nome, Cognome, Numero (formato da una sola cifra)'
                    else:
                        string = "Richiesta effettuata con successo,riceverai una notifica appena la richiesta avrà un esito"
                        f.comunicate_admin(register, self)
        f.bot.sendMessage(chat_id, string, reply_markup=rp)
        #if string != 'Cosa vuoi fare ?' and not workingTicket:
        #    string, rp = f.start(None)
        #    f.bot.sendMessage(chat_id, string, reply_markup=rp)
        #keyboard = InlineKeyboardMarkup(inline_keyboard=[
        #    [InlineKeyboardButton(text='Approvo', callback_data='approve'),
        #     InlineKeyboardButton(text='NON Approvo', callback_data='disapprove')],
        #    [InlineKeyboardButton(text='Time', callback_data='time')],
        #])
        #bot.sendMessage(chat_id, 'Use inline keyboard', reply_markup=keyboard)

    f.batch()#batch control for registered users
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,#call thread for every msg
                      'callback_query': f.on_callback_query}).run_as_thread()
    print('Listening ...')

    while 1:
        time.sleep(10)