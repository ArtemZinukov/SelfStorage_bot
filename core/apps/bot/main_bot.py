from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from environs import Env


env = Env()
env.read_env()
token = env.str("TG_BOT_TOKEN")
bot = TeleBot(token)


def save_name(message):
    name = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Отлично, {name}. Теперь укажите свой адрес')
    bot.register_next_step_handler(message, save_address)


def save_address(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Отлично, данные получены')


def send_message_with_file(message, file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        text = file.read()
    bot.send_message(message.chat.id, text)


def send_order_message(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Бесплатная доставка из дома')
    markup.row('Выбрать адрес приема вещей')
    markup.row('Вернуться на главную')
    tariff_message = '''
Тарифы:
    Мало вещей:
        0.5 м³ - <b>1800 руб. в месяц</b> 
        (Поместятся детские игрушки и коляска, до пяти коробок или одна стиральная машина.)  
        1.5 м³ - <b>2900 руб. в месяц</b>
        (Подойдет для хранения мелкой бытовой техники) 
        3 м³ - <b>4900 руб. в месяц</b>
        (Достаточно места для некрупной мебели: стульев, комода и телевизора.) 
    Много вещей:
        6 м³ - <b>8800 руб. в месяц</b>
        (Поместятся крупные вещи и мебель: угловой диван и двухспальная кровать с матрасом.)  
        9 м³ - <b>12900 руб. в месяц</b>
        (Много места. Влезут несколько больших шкафов, кухня, крупная бытовая техника.) 
        18 м³ - <b>18900 руб. в месяц</b>
        (Полноценный склад: достаточно места для содержимого нескольких комнат.) 
'''
    order_message = '''
Выберите способ доставки:
'''
    bot.send_message(message.chat.id, tariff_message, parse_mode='HTML')
    bot.send_message(message.chat.id, order_message, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
def send_back_to_main(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Условия хранения')
    markup.row('Список запрещенных вещей')
    markup.row('Сделать заказ')
    back_to_main_message = '''
На главную
'''
    bot.send_message(message.chat.id, back_to_main_message, reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Условия хранения')
    markup.row('Список запрещенных вещей')
    markup.row('Сделать заказ')
    start_message = '''
Привет Мы SelfStorage!
Когда мы понадобимся:

1.Для ваших личных вещей
2.Для бизнеса
3.Ремонт
4.Переезд
5.И всё, что угодно
'''
    bot.send_message(message.chat.id, start_message, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Список запрещенных вещей')
def send_prohibited_items(message):
    send_message_with_file(message, 'core/apps/bot/prohibited_items.txt')


@bot.message_handler(func=lambda message: message.text == 'Условия хранения')
def send_store_conditions(message):
    send_message_with_file(message, 'core/apps/bot/store_conditions.txt')


@bot.message_handler(func=lambda message: message.text == 'Сделать заказ')
def send_order(message):
    send_order_message(message)


@bot.message_handler(func=lambda message: message.text == 'Бесплатная доставка из дома')
def send_free_delivery(message):
    free_delivery_message = '''
Бесплатная доставка из дома!
Введите ваш адрес и мы доставим ваш заказ бесплатно.
'''
    bot.send_message(message.chat.id, free_delivery_message)


@bot.message_handler(func=lambda message: message.text == 'Выбрать адрес приема вещей')
def send_address_choice(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    storage_adress_message = '''
Мы находимся по адресу:
    1. Мясницкая 60
    2. Остоженка 62
    3. Херсонская улица 38
'''
    bot.send_message(message.chat.id, storage_adress_message, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
def send_back_to_main(message):
    send_back_to_main(message)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()

