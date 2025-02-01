import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения выбранных цветов маркеров для каждого пользователя
user_colors = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
Доступные команды:
/start - Начать работу с ботом.
/help - Получить список команд.
/show_city <название города> - Показать город на карте.
/remember_city <название города> - Сохранить город в список посещенных.
/show_my_cities - Показать все сохраненные города.
/set_color <цвет> - Выбрать цвет маркеров (например, red, blue, green).
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['set_color'])
def handle_set_color(message):
    user_id = message.chat.id
    color = message.text.split()[-1].lower()
    available_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    
    if color in available_colors:
        user_colors[user_id] = color
        bot.send_message(user_id, f"Цвет маркеров изменен на {color}.")
    else:
        bot.send_message(user_id, "Недопустимый цвет. Доступные цвета: red, blue, green, yellow, purple, orange.")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    user_id = message.chat.id
    marker_color = user_colors.get(user_id, 'blue')  # По умолчанию синий цвет
    manager.create_graph(f'{user_id}.png', [city_name], marker_color)

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
        marker_color = user_colors.get(message.chat.id, 'blue')  # По умолчанию синий цвет
        manager.create_graph(f'{message.chat.id}_cities.png', cities, marker_color)
        with open(f'{message.chat.id}_cities.png', 'rb') as map:
            bot.send_photo(message.chat.id, map)
    else:
        bot.send_message(message.chat.id, "Вы еще не сохранили ни одного города.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    city_name = message.text.strip()
    user_id = message.chat.id
    marker_color = user_colors.get(user_id, 'blue')  # По умолчанию синий цвет

    if manager.get_coordinates(city_name):
        manager.create_graph(f'{user_id}.png', [city_name], marker_color)
        with open(f'{user_id}.png', 'rb') as map:
            bot.send_photo(user_id, map)
    else:
        bot.send_message(user_id, "Такого города я не знаю. Убедись, что он написан на английском!")

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()