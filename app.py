from flask import Flask, request, render_template, redirect
import telegram
from credentials import bot_token, URL
from flask_sqlalchemy import SQLAlchemy

global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    chat = db.Column(db.Text)
    mode = db.Column(db.Text, default = 'nothing')

    def __repr__(self):
        return '<Flora %r>' % self.id


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    user_id = update.message.chat.first_name
    user_idd = update.message.chat.username

    text = update.message.text.encode('utf-8').decode()

    users = User.query.all()
    a = 0
    for i in users:
        if str(chat_id) in str(i.chat):
            a = 1
    if a == 0:
        user = User(chat=chat_id,
                    user=user_id)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            print('no')

    if text == "/start":
        # print the welcoming message
        bot_welcome = '''
Assalomu aleykum
    '''
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    elif text == "/help":
        bot_help = '''
Turlarni izlash bo'yicha tavsiyalar.
Turni izlash uchun uning lotin (masalan: Allium karataviense), rus (masalan: Лук каратавский) yoki o'zbek (Masalan: Қоратоғ пиёзи) tillarida nomini kiriting.
Agar izlash natija bermagan bo'lsa, turning nomini to'g'ri kiritganingizni tekshirib ko'ring.
/help - Izlash bo'yicha tavsiyalar
/donate - Bot rivojiga yordam berish
/random - Tasodifiy turni ko'rish
Agar bunda ham izlash natija bermagan bo'lsa, va siz ushbu tur O'zbekiston florasida uchrashiga amin bo'lsangiz biz bilan bog'laning: @KhRustamov
        '''
        bot.sendMessage(chat_id=chat_id, text=bot_help, reply_to_message_id=msg_id)

    elif text == "/onto":
        user = User.query.get(chat=chat_id, user=user_id)
        user.mode = 'onto'
        try:
            db.session.commit()
        except:
            print('no')
        bot_help = 'Rejim: ontogenetik parametrlarni tahlili'
        bot.sendMessage(chat_id=chat_id, text=bot_help, reply_to_message_id=msg_id)

    elif text == "/morpho":
        user = User.query.get(chat=chat_id, user=user_id)
        user.mode = 'morpho'
        try:
            db.session.commit()
        except:
            print('no')
        bot_help = 'Rejim: morfometrik parametrlarni tahlili'
        bot.sendMessage(chat_id=chat_id, text=bot_help, reply_to_message_id=msg_id)

    else:
        user = User.query.get(chat=chat_id, user=user_id)
        if user.mode == 'onto':
            parameters = text.split(' ')
            try:
                delta_coef = [0.0025, 0.0067, 0.0180, 0.0474, 0.1192, 0.2689, 0.5, 0.7311, 0.8808, 0.8808, 0.9820]
                omega_coef = [0.0099, 0.0266, 0.0707, 0.1807, 0.4200, 0.7864, 1.0, 0.7864, 0.4200, 0.1807, 0.0707]
                Delta = sum(i * m for i, m in zip(parameters, delta_coef)) / sum(parameters)
                Omega = sum(i * m for i, m in zip(parameters, omega_coef)) / sum(parameters)
                if Omega < 0.60 and Delta < 0.35:
                    bot_help = "Ценопопуляция молодая, Δ=%s, ω=%s" % (str(Delta), str(Omega))  # molodoy
                elif Omega >= 0.60 and Delta < 0.35:
                    bot_help = "Ценопопуляция зреющая, Δ=%s, ω=%s" % (str(Delta), str(Omega))  # zreyushiy
                elif Omega < 0.70 and 0.35 <= Delta < 0.55:
                    bot_help = "Ценопопуляция переходная, Δ=%s, ω=%s" % (str(Delta), str(Omega))  # perehodniy
                elif Omega >= 0.70 and 0.35 <= Delta < 0.55:
                    bot_help = "Ценопопуляция зрелая, Δ=%s, ω=%s" % (str(Delta), str(Omega))  # zreliy
                elif Omega < 0.60 and Delta >= 0.55:
                    bot_help = "Ценопопуляция старая, Δ=%s, ω=%s" % (str(Delta), str(Omega))  # stariy
                elif Omega > 0.60 and Delta >= 0.55:
                    bot_help = "Ценопопуляция стареющая, Δ=%s, ω=%s" % (str(Delta), str(Omega))  # stareyushiy
                else:
                    bot_help = "Ошибка! Дельта и Омега числа меньше 1"
            except:
                bot_help = '''Общее количество особей не совпадает с количеством введенных данных(сумма
                           онтогенетических состояний не равна введеному количеству всех особей)'''
            bot.sendMessage(chat_id=chat_id, text=bot_help, reply_to_message_id=msg_id)

    return "ok"


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/send', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        TOKEN = bot_token
        bot = telegram.Bot(token=TOKEN)
        message = str(request.form['message'])
        users = User.query.all()
        for i in users:
            try:
                chat_id = i.chat
                bot.sendMessage(chat_id=chat_id, text=message)
            except:
                pass
        return redirect("/")
    else:
        return render_template("send.html")


if __name__ == '__main__':
    app.run(debug=True)