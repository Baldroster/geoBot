import telebot
import requests

bot = telebot.TeleBot('')
geotrackingToken = ''
state = 0


@bot.message_handler(commands=['start'])
@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот. Отправь мне геолокацию, и я помогу определить тебе адрес\n ')


@bot.message_handler(content_types=['location'])
def send_text(message):
    params = {'key': geotrackingToken,
              'lat': message.location.latitude,
              'lon': message.location.longitude,
              'format': 'json'
              }
    r = requests.get('https://eu1.locationiq.com/v1/reverse.php', params)
    if r.status_code == 200:
        data = r.json()
        message_text = "Ваш адрес:  {0}, {1}, {2}, {3}, ".format(data['address']['country'],
                                                                    data['address']['state'], data['address']['city'],
                                                                    data['address']['city_district'])

        if 'house_number' in data['road']:
            message_text += ', {0}'.format(data['address']['road'])

        if 'house_number' in data['address']:
            message_text += ', {0}'.format(data['address']['house_number'])
        bot.send_message(message.chat.id, message_text)


bot.polling()
