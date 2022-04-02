from flask import Flask, request, render_template, redirect
import telegram
from credentials import bot_token, URL
from flask_sqlalchemy import SQLAlchemy

global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    user_id = update.message.chat.first_name
    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    print("got text message :", text)

    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
        Assalomu aleykum"""
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
 
   
    else:
        if True:
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
    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    app.run(debug=True)
