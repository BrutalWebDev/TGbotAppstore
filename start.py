import telebot
import config
import qiwiPayKey
import re
from time import sleep
from pyqiwip2p import QiwiP2P

bot = telebot.TeleBot(config.tokenBot)
p2p = QiwiP2P(auth_key=config.secret_p2p)

api_access_token = config.tokenQIWI #токен киви
prv_id = '23554' #номер провайдера appstore
comment = ' '
lifetime = 5 #Время жизни формы оплаты


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Привет!")
    bot.send_message(message.chat.id, "Я пришлю вам код карты для пополнения баланса в магазине App Store")    
    bot.send_message(message.chat.id,"Введите сумму для зачисления от 200 до 5000")

    @bot.message_handler(content_types=['text'])
    def ammount(message):
    
        words = message.text
        if config.flag == 0 and words[0] != '+' and words.isdigit(): # если этап ввода денег и если вначале нет + и если текст может быть int

            config.amm = int(message.text)

            if config.amm < 200 or config.amm > 5000: 
                bot.send_message(message.chat.id,"Введите сумму для зачисления от 200 до 5000")
            else:
                bot.send_message(message.chat.id,"Далее введите ваш российский номер телефона начиная с +7")
                config.flag = 1 

        elif config.flag == 1 and words[0] == '+': # если этап ввода телефона и если вначале есть +

                numb_phone = message.text

                result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', numb_phone)
                
                if result:
                    config.to_account = numb_phone
                    comment = "Карта App Store для " + numb_phone
                    config.bill = p2p.bill(amount=config.amm+10, lifetime=lifetime, comment=comment)
                    url =  p2p.check(bill_id = config.bill.bill_id).pay_url
                    bot.send_message(message.chat.id,f"Ваша ссылка для оплаты: {url} после подтверждения, поступит SMS с кодом карты для App Store. В сумму платежа встроена комиссия 10 руб.")
                    bot.send_message(message.chat.id,"Ожидание платежа..")
                    config.flag = 2
                    while p2p.check(bill_id = config.bill.bill_id).status != 'PAID':
                        sleep(5)
                        config.counters += 1
                        if p2p.check(bill_id = config.bill.bill_id).status == 'PAID':
                            bot.send_message(message.chat.id,"Платеж зачислен, ожидайте SMS. Чтобы оплатить новую карту App Store, введите /new")
                            sleep(2)
                            qiwiPayKey.pay_simple_prv(api_access_token, prv_id, config.to_account, config.amm-10)
                        elif config.counters == 60:
                            bot.send_message(message.chat.id,"Время на оплату вышло. Для получения новой карты App Store, введите /new")
                            config.flag = 0
                            config.counters = 0
                            break
                else:
                    bot.send_message(message.chat.id,"Не правильно набран номер, введите ваш российский номер телефона начиная с +7")

        elif config.flag == 1: # если этап ввода телефона и вначале нет +
            bot.send_message(message.chat.id,"Введите ваш российский номер телефона начиная с +7")
        elif config.flag == 2 and words == "/new":
            config.flag = 0
            bot.send_message(message.chat.id,"Введите сумму для зачисления от 200 до 5000")
        elif config.flag == 2:
            bot.send_message(message.chat.id,"Для получения новой карты App Store, введите /new")
        else: 
            bot.send_message(message.chat.id,"Введите сумму для зачисления от 200 до 5000")

bot.polling(non_stop=True)