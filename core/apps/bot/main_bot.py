from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from environs import Env
import re
from core.apps.bot.models import Order
import datetime
import qrcode
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


env = Env()
env.read_env()
token = env.str("TG_BOT_TOKEN")
bot = TeleBot(token)


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


def get_user_data_without_metering(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')

    def ask_name(message):
        bot.send_message(message.chat.id, 'Введите ваше имя', reply_markup=markup)
        bot.register_next_step_handler(message, handle_name)

    def handle_name(message):
        client_name = Order.objects.create(client_name=message.text)
        client_name.save()
        ask_email(message)

    def ask_email(message):
        bot.send_message(message.chat.id, 'Введите вашу электронную почту:', reply_markup=markup)
        bot.register_next_step_handler(message, handle_email)

    def handle_email(message):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, message.text):
            order = Order.objects.last()
            order.email = message.text
            order.save()
            ask_phone(message)
        else:
            bot.send_message(message.chat.id, 'Некорректный формат электронной почты. Пожалуйста, введите снова:',
                             reply_markup=markup)
            bot.register_next_step_handler(message, handle_email)

    def ask_phone(message):
        bot.send_message(message.chat.id, 'Введите ваш номер телефона: (Например: 78521503215)',
                         reply_markup=markup)
        bot.register_next_step_handler(message, handle_phone)

    def handle_phone(message):
        phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        if re.match(phone_pattern, message.text):
            order = Order.objects.last()
            order.phone_number = message.text
            order.save()
            ask_address(message)
        else:
            bot.send_message(message.chat.id, 'Некорректный формат номера телефона. Пожалуйста, введите снова:',
                             reply_markup=markup)
            bot.register_next_step_handler(message, handle_phone)

    def ask_address(message):
        bot.send_message(message.chat.id, 'Введите ваш адрес:', reply_markup=markup)
        bot.register_next_step_handler(message, handle_address)

    def handle_address(message):
        order = Order.objects.last()
        order.address = message.text
        order.save()
        generate_qr_code(order.pk)
        add_date()
        bot.send_message(message.chat.id, f'Заказ оформлен. № заказа {order.pk}', reply_markup=markup)

    def generate_qr_code(message):
        order = Order.objects.last()
        img = qrcode.make(message)
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        order.qr_code.save(f'qr_code_{order.pk}.png',
                           InMemoryUploadedFile(buffer, None, 'qr_code.png', 'image/png',
                                                buffer.tell(), None))
        order.save()

    def add_date():
        order = Order.objects.last()
        current_date = datetime.date.today()
        order.date = current_date
        order.save()

    ask_name(message)


def get_user_data_with_metering(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')

    def get_user_data(message):
        get_user_data_without_metering(message)
        bot.register_next_step_handler(message, ask_volume)

    def ask_volume(message):
        bot.send_message(message.chat.id, 'Введите объем вещей в м³:', reply_markup=markup)
        bot.register_next_step_handler(message, handle_volume)

    def handle_volume(message):
        try:
            volume = float(message.text)
            if volume <= 0:
                bot.send_message(message.chat.id, 'Объем должен быть положительным числом.')
                ask_volume(message)
            else:
                order = Order.objects.last()
                order.volume = volume
                order.save()
        except ValueError:
            bot.send_message(message.chat.id, 'Объем должен быть числом.')
            ask_volume(message)

    get_user_data(message)


@bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
def send_back_to_main(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Условия хранения')
    markup.row('Список запрещенных вещей')
    markup.row('Сделать заказ')
    markup.row('Получить свой заказ')
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
    markup.row('Получить свой заказ')
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
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Самостоятельно сделаю замер', 'Замер сделает доставщик')
    markup.row('Вернуться на главную')
    free_delivery_message = '''
Бесплатная доставка из дома!
Выберите способ замера вещей:
'''
    bot.send_message(message.chat.id, free_delivery_message, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Самостоятельно сделаю замер')
def get_user(message):
    get_user_data_with_metering(message)


@bot.message_handler(func=lambda message: message.text == 'Замер сделает доставщик')
def get_user(message):
    get_user_data_without_metering(message)


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


@bot.message_handler(func=lambda message: message.text == 'Получить свой заказ')
def get_orders(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Введите номер вашего заказа:', reply_markup=markup)
    bot.register_next_step_handler(message, show_qr_code)


def show_qr_code(message):
    order_id = int(message.text)
    order = Order.objects.get(pk=order_id)
    img = qrcode.make(str(order.pk))
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    bot.send_photo(message.chat.id, buffer.getvalue())
    bot.send_message(message.chat.id, 'Вы можете вернуть свои вещи, если срок аренды не истек')


@bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
def send_back_to_main(message):
    send_back_to_main(message)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()
