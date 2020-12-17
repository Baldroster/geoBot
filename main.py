import telebot
from lxml import etree
from telebot import types

bot = telebot.TeleBot('KEY')

session = {}


@bot.message_handler(commands=['start'])
@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот-конвертер.Чтобы перевести валюту введи /convert\n ')


@bot.message_handler(commands=['convert'])
def start_message(message):
    session[message.chat.id] = {}
    data = etree.parse("http://www.cbr.ru/scripts/XML_daily.asp")
    result = [node.text.strip()
              for node in data.xpath("//CharCode")]

    keyboard = types.InlineKeyboardMarkup()

    for each in result:
        keyboard.row(types.InlineKeyboardButton(each, callback_data='first' + each))
    bot.send_message(message.chat.id, text="Выберите конвертируемую валюту", reply_markup=keyboard)

    print(result)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = etree.parse("http://www.cbr.ru/scripts/XML_daily.asp")
    if call.message:
        if 'first' in call.data:
            session[call.message.chat.id]['fromVal'] = call.data[5:]
            result = [node.text.strip()
                      for node in data.xpath("//CharCode")]
            keyboard = types.InlineKeyboardMarkup()
            for each in result:
                keyboard.row(types.InlineKeyboardButton(each, callback_data='second' + each))
            bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(call.message.chat.id, text="Выберите валюту,в которую конвертируем валюту",
                             reply_markup=keyboard)
        elif 'second' in call.data:
            session[call.message.chat.id]['toVal'] = call.data[6:]
            bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(call.message.chat.id, text="Введите количество переводимой валюты")
            session[call.message.chat.id]['convertMode'] = True

    @bot.message_handler(content_types=['text'])
    def count(message):
        if session[message.chat.id]['convertMode'] == True:
            if message.text.isnumeric():
                data = etree.parse("http://www.cbr.ru/scripts/XML_daily.asp")
                value1 = [node.text.strip()
                          for node in data.xpath("//CharCode[text()='{0}']/../Value".format(
                        session[call.message.chat.id]['fromVal']))][0]
                value2 = [node.text.strip()
                          for node in
                          data.xpath("//CharCode[text()='{0}']/../Value".format(
                              session[call.message.chat.id]['toVal']))][0]
                nominal1 = [node.text.strip()
                          for node in
                          data.xpath("//CharCode[text()='{0}']/../Nominal".format(
                              session[call.message.chat.id]['fromVal']))][0]
                nominal1 = 1 if nominal1 is None else nominal1
                nominal2 = [node.text.strip()
                            for node in
                            data.xpath("//CharCode[text()='{0}']/../Nominal".format(
                                session[call.message.chat.id]['toVal']))][0]
                nominal2 = 1 if nominal2 is None else nominal2
                result = float(message.text.replace(',', '.')) * float(value1.replace(',', '.')) /float(nominal1.replace(',', '.')) / float(value2.replace(',', '.')) * float(nominal2.replace(',', '.'))
                bot.send_message(message.chat.id, text="{0} {1} = {2} {3}".format(message.text,session[call.message.chat.id]['fromVal'],result,session[call.message.chat.id]['toVal']))
                session[call.message.chat.id]={}

            else:
                bot.send_message(message.chat.id, text="Введите число!")


bot.polling()
