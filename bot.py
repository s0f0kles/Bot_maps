import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
Доступные команды:
/start - Начать работу с ботом и получить приветственное сообщение.
/help - Получить список доступных команд.
/show_city <название города> - Отобразить указанный город на карте.
/remember_city <название города> - Сохранить город в список посещенных.
/show_my_cities - Показать все сохраненные города.

Также ты можешь просто написать название города, и я покажу его на карте!
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    user_id = message.chat.id
    manager.create_graph(f'{user_id}.png', [city_name])

    with open(f'{user_id}.png', 'rb') as map:
        bot.send_photo(user_id, map)

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if cities:
        manager.create_graph(f'{message.chat.id}_cities.png', cities)
        with open(f'{message.chat.id}_cities.png', 'rb') as map:
            bot.send_photo(message.chat.id, map)
    else:
        bot.send_message(message.chat.id, "Вы еще не сохранили ни одного города.")

@bot.message_handler(func=lambda message: True)  # Обработчик для текстовых сообщений
def handle_text(message):
    city_name = message.text.strip()  # Убираем лишние пробелы
    user_id = message.chat.id

    # Проверяем, есть ли город в базе данных
    if manager.get_coordinates(city_name):
        manager.create_graph(f'{user_id}.png', [city_name])
        with open(f'{user_id}.png', 'rb') as map:
            bot.send_photo(user_id, map)
    else:
        bot.send_message(user_id, "Такого города я не знаю. Убедись, что он написан на английском!")

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()