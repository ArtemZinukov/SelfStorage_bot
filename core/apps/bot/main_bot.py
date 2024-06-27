from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from environs import Env
import telebot
from telebot import types


env = Env()
env.read_env()
token = env.str("TG_BOT_TOKEN")
bot = telebot.TeleBot(token)
# bot = TeleBot(token).


def save_name(message):
    name = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Отлично, {name}. Теперь укажите свой адрес')
    bot.register_next_step_handler(message, save_address)


def save_address(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Отлично, данные получены')


@bot.message_handler(content_types=['text'])
def hear_menu(message):
    if message.text == '/start':
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton(text='Тарифы', callback_data='prefix:Тарифы'))
        inline_markup.add(types.InlineKeyboardButton(text='Условия хранения', callback_data='prefix:Условия хранения'))
        inline_markup.add(types.InlineKeyboardButton(text='Заказать бокс', callback_data='prefix:Заказать бокс'))
        bot.send_message(message.chat.id, f'Привет!\nЭто сервис хранения вещей с доставкой.\nЗаберем вещи на наш склад, сохраним и привезем обратно',
                         reply_markup=inline_markup)
    elif message.text:
        save_name(message)



@bot.callback_query_handler(func=lambda call: call.data.split(":")[0] == 'prefix')
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    data_ = call.data.split(":")[1]
    if data_ == 'Заказать бокс':
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton(text='Привезти самому', callback_data=f"prefix2:Привезти самому"))
        inline_markup.add(types.InlineKeyboardButton(text='Бесплатная доставка из дома', callback_data=f"prefix2:Бесплатная доставка из дома"))
        inline_markup.add(types.InlineKeyboardButton(text='👈 назад 👈', callback_data="prefix2:назад"))
        bot.edit_message_text('Выберите подходящий вариант', call.message.chat.id, call.message.message_id,
                              reply_markup=inline_markup)

@bot.callback_query_handler(func=lambda call: call.data.split(":")[0] == "prefix2")
def querry_handler2(call):
    data_ = call.data.split(":")[1]
    inline_markup = types.InlineKeyboardMarkup()
    if data_ == 'Привезти самому':
        inline_markup.add(types.InlineKeyboardButton(text='👈 назад 👈', callback_data="prefix3:назад"))
        bot.edit_message_text(f'Пункты приема:\nАдрес_1\nАдрес_2\nАдрес_3\n', call.message.chat.id, call.message.message_id, reply_markup=inline_markup)

    elif data_ == 'Бесплатная доставка из дома':
        bot.send_message(call.message.chat.id, f'Введите ваше имя')






    elif data_ == 'назад':
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton(text='Тарифы', callback_data='prefix:Тарифы'))
        inline_markup.add(types.InlineKeyboardButton(text='Условия хранения', callback_data='prefix:Условия хранения'))
        inline_markup.add(types.InlineKeyboardButton(text='Заказать бокс', callback_data='prefix:Заказать бокс'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data.split(":")[0] == "prefix3")
def querry_handler2(call):
    data_ = call.data.split(":")[1]
    if data_ == 'назад':
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton(text='Привезти самому', callback_data=f"prefix2:Привезти самому"))
        inline_markup.add(types.InlineKeyboardButton(text='Бесплатная доставка из дома',
                                                     callback_data=f"prefix2:Бесплатная доставка из дома"))
        inline_markup.add(types.InlineKeyboardButton(text='👈 назад 👈', callback_data="prefix2:назад"))
        bot.edit_message_text('Выберите подходящий вариант', call.message.chat.id, call.message.message_id,
                              reply_markup=inline_markup)





# def send_message_with_file(message, file_name):
#     with open(file_name, 'r', encoding='utf-8') as file:
#         text = file.read()
#     bot.send_message(message.chat.id, text)
#
#
# def send_order_message(message):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.row('Бесплатная доставка из дома')
#     markup.row('Выбрать адрес приема вещей')
#     markup.row('Вернуться на главную')
#     order_message = '''
# Выберите способ доставки:
# '''
#     bot.send_message(message.chat.id, order_message, reply_markup=markup)
#
#
# @bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
# def send_back_to_main(message):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.row('Условия хранения')
#     markup.row('Список запрещенных вещей')
#     markup.row('Сделать заказ')
#     back_to_main_message = '''
# Вернуться на главную:
# '''
#     bot.send_message(message.chat.id, back_to_main_message, reply_markup=markup)
#
#
# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.row('Условия хранения')
#     markup.row('Список запрещенных вещей')
#     markup.row('Сделать заказ')
#     start_message = '''
# Привет Мы SelfStorage!
# Когда мы понадобимся:
#
# 1.Для ваших личных вещей
# 2.Для бизнеса
# 3.Ремонт
# 4.Переезд
# 5.И всё, что угодно
# '''
#     bot.send_message(message.chat.id, start_message, reply_markup=markup)
#
#
# @bot.message_handler(func=lambda message: message.text == 'Список запрещенных вещей')
# def send_prohibited_items(message):
#     send_message_with_file(message, 'prohibited_items.txt')
#
#
# @bot.message_handler(func=lambda message: message.text == 'Условия хранения')
# def send_store_conditions(message):
#     send_message_with_file(message, 'store_conditions.txt')
#
#
# @bot.message_handler(func=lambda message: message.text == 'Сделать заказ')
# def send_order(message):
#     send_order_message(message)
#
#
# @bot.message_handler(func=lambda message: message.text == 'Бесплатная доставка из дома')
# def send_free_delivery(message):
#     free_delivery_message = '''
# Бесплатная доставка из дома!
# Введите ваш адрес и мы доставим ваш заказ бесплатно.
# '''
#     bot.send_message(message.chat.id, free_delivery_message)
#
#
# @bot.message_handler(func=lambda message: message.text == 'Выбрать адрес приема вещей')
# def send_address_choice(message):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.row('Мясницкая 60')
#     markup.row('Остоженка 62')
#     markup.row('Херсонская улица 38')
#     markup.row('Вернуться на главную')
#     bot.send_message(message.chat.id, 'Выберите адрес приема вещей:', reply_markup=markup)
#
#
# @bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
# def send_back_to_main(message):
#     send_back_to_main(message)
#
#
# def main():
#     bot.infinity_polling()
#
#
# if __name__ == "__main__":
#     main()

