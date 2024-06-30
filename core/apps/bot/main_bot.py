from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from environs import Env
import re
from core.apps.bot.models import Order
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from core.apps.bot.count_refferals import count_referrals, count_referrals_message

env = Env()
env.read_env()
token = env.str("TG_BOT_TOKEN")
bot = TeleBot(token)


def send_message_with_file(message, file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        text = file.read()
    bot.send_message(message.chat.id, text, parse_mode='HTML')


def send_pd_consent_file(message, file_name):
    with open(file_name, 'rb') as file:
        bot.send_document(message.chat.id, file)


def send_order_message(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Бесплатная доставка из дома')
    markup.row('Выбрать адрес приема вещей')
    markup.row('Вернуться на главную')
    tariff_message = '''
Тарифы на хранение вещей

<b>Мало вещей</b>
• 0.5 м³: 1800 руб. в месяц (детские игрушки, коляска, до 5 коробок или стиральная машина)
• 1.5 м³: 2900 руб. в месяц (мелкая бытовая техника)
• 3 м³: 4900 руб. в месяц (некрупная мебель: стулья, комод, телевизор)

<b>Много вещей</b>
• 6 м³: 8800 руб. в месяц (крупные вещи и мебель: угловой диван, двухспальная кровать с матрасом)
• 9 м³: 12900 руб. в месяц (много места: несколько больших шкафов, кухня, крупная бытовая техника)
• 18 м³: 18900 руб. в месяц (полноценный склад: содержимое нескольких комнат)

Выберите способ доставки:
'''
    bot.send_message(message.chat.id, tariff_message, parse_mode='HTML', reply_markup=markup)


def ask_name(message):
    bot.send_message(message.chat.id, 'Введите ваше имя')
    bot.register_next_step_handler(message, handle_name)


def handle_name(message):
    client_name = Order.objects.create(client_name=message.text)
    client_name.save()


def ask_volume(message):
    bot.send_message(message.chat.id, 'Введите объем вещей в м³:')
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
            ask_email(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Объем должен быть числом.')
        ask_volume(message)


def ask_email(message):
    bot.send_message(message.chat.id, 'Введите вашу электронную почту:')
    bot.register_next_step_handler(message, handle_email)


def handle_email(message):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[+a-zA-Z0-9.-]\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, message.text):
        order = Order.objects.last()
        order.email = message.text
        order.save()
        ask_phone(message)
    else:
        bot.send_message(message.chat.id, 'Некорректный формат электронной почты. Пожалуйста, введите снова:')
        bot.register_next_step_handler(message, handle_email)


def ask_phone(message):
    bot.send_message(message.chat.id, 'Введите ваш номер телефона: (Например: 78521503215)')
    bot.register_next_step_handler(message, handle_phone)


def handle_phone(message):
    phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    if re.match(phone_pattern, message.text):
        order = Order.objects.last()
        order.phone_number = message.text
        order.save()
        ask_address(message)
    else:
        bot.send_message(message.chat.id, 'Некорректный формат номера телефона. Пожалуйста, введите снова:')
        bot.register_next_step_handler(message, handle_phone)


def ask_address(message):
    bot.send_message(message.chat.id, 'Введите ваш адрес:')
    bot.register_next_step_handler(message, handle_address)


def handle_address(message):
    order = Order.objects.last()
    order.address = message.text
    order.save()
    generate_qr_code(order.pk)
    add_date()
    bot.send_message(message.chat.id, f'Заказ оформлен. № заказа {order.pk}')


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
    current_date = datetime.now()
    format_current_date = current_date.strftime("%m/%d/%Y %H:%M:%S")
    order.date = format_current_date
    order.delivery = True
    delta = timedelta(minutes=5)
    end_date = current_date + delta
    format_end_date = end_date.strftime("%m/%d/%Y %H:%M:%S")
    order.end_date = format_end_date
    order.save()


def get_user_data_without_metering(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    ask_name(message)
    bot.register_next_step_handler(message, ask_email)


def get_user_data_with_metering(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    ask_name(message)
    bot.register_next_step_handler(message, ask_volume)


def send_back_to_main(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Условия хранения', 'Список запрещенных вещей')
    markup.row('Сделать заказ', 'Получить свой заказ')
    back_to_main_message = '''
Выберите действие: 
'''
    bot.send_message(message.chat.id, back_to_main_message, reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Вконтакте", "Instagram")
    markup.row("Яндекс", "От знакомых")
    start_message = '''
Привет!
Мы <b>SelfStorage</b> - ваше надежное пространство для хранения вещей!

Когда вам может потребоваться наша помощь:

    • для хранения личных вещей;
    • для бизнеса;
    • при ремонте;
    • при переезде;
    • и в любых других ситуациях, когда вам нужно дополнительное хранилище.

Откуда вы узнали о нас?
'''
    bot.send_message(message.chat.id, start_message, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == 'Вконтакте')
def numbers_of_transitions_vk(message):
    count_referrals(message.text)
    bot.send_message(message.chat.id, "Спасибо, за ответ!")
    send_back_to_main(message)


@bot.message_handler(func=lambda message: message.text == 'Instagram')
def numbers_of_transitions_vk(message):
    count_referrals(message.text)
    bot.send_message(message.chat.id, "Спасибо, за ответ!")
    send_back_to_main(message)


@bot.message_handler(func=lambda message: message.text == 'Яндекс')
def numbers_of_transitions_vk(message):
    count_referrals(message.text)
    bot.send_message(message.chat.id, "Спасибо, за ответ!")
    send_back_to_main(message)


@bot.message_handler(func=lambda message: message.text == 'От знакомых')
def numbers_of_transitions_vk(message):
    count_referrals(message.text)
    bot.send_message(message.chat.id, "Спасибо, за ответ!")
    send_back_to_main(message)


@bot.message_handler(func=lambda message: message.text == 'Админка')
def enter_to_admin_panel(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Получить число переходов с рекламы")
    markup.row("Посмотреть заказы с доставкой")
    markup.row("Посмотреть просроченные заказы")
    markup.row("Вернуться на главную")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Получить число переходов с рекламы')
def get_number_conversions_ads(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("от Вконтакте", "от Instagram")
    markup.row("от Яндекс", "Вернуться на главную")
    bot.send_message(message.chat.id, "Выберите рекламу", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'от Вконтакте')
def handle_vk_referrals(message):
    ads_source = "Вконтакте"
    number_of_jumps = count_referrals_message(ads_source)
    bot.send_message(message.chat.id, f"Количество переходов из {ads_source} = {number_of_jumps}")


@bot.message_handler(func=lambda message: message.text == 'от Instagram')
def handle_vk_referrals(message):
    ads_source = "Instagram"
    number_of_jumps = count_referrals_message(ads_source)
    bot.send_message(message.chat.id, f"Количество переходов из {ads_source} = {number_of_jumps}")


@bot.message_handler(func=lambda message: message.text == 'от Яндекс')
def handle_vk_referrals(message):
    ads_source = "Яндекс"
    number_of_jumps = count_referrals_message(ads_source)
    bot.send_message(message.chat.id, f"Количество переходов из {ads_source} = {number_of_jumps}")


@bot.message_handler(func=lambda message: message.text == 'Посмотреть заказы с доставкой')
def get_orders_with_delivery(message):
    orders_with_delivery = Order.objects.filter(delivery=True)
    bot.send_message(message.chat.id, "Заказы оформленные с доставкой:")
    for order in orders_with_delivery:
        bot.send_message(message.chat.id, f"Заказ номер {order.pk}: Номер телефона - {order.phone_number}, "
                                          f"адрес - {order.address}")


@bot.message_handler(func=lambda message: message.text == 'Список запрещенных вещей')
def send_prohibited_items(message):
    send_message_with_file(message, 'core/apps/bot/prohibited_items.txt')


@bot.message_handler(func=lambda message: message.text == 'Условия хранения')
def send_store_conditions(message):
    send_message_with_file(message, 'core/apps/bot/store_conditions.txt')


@bot.message_handler(func=lambda message: message.text == 'Сделать заказ')
def get_personal_data_consent(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Согласен')
    markup.row('Вернуться на главную')
    send_pd_consent_file(message, 'core/apps/bot/pd_consent.pdf')
    message_text = '''
Ознакомьтесь с файлом и подтвердите согласие.
"Вернуться на главную" означает отказ от обработки персональных данных.   
'''
    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Согласен')
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
Адреса наших складов:

    1. Мясницкая,60
    2. Остоженка,62
    3. Херсонская улица,38

Замер вещей производится непосредственно на складе.
'''
    bot.send_message(message.chat.id, storage_adress_message, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Получить свой заказ')
def get_orders(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Забрать полный комплект вещей')
    markup.row('Забрать частичный комплект вещей')
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Забрать полный комплект вещей')
def get_full_order(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Заберу сам')
    markup.row('Оформить доставку')
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Выберите способ получения вещей:', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Заберу сам')
def get_order_myself(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Введите номер вашего заказа:', reply_markup=markup)
    bot.register_next_step_handler(message, show_qr_code)


@bot.message_handler(func=lambda message: message.text == 'Оформить доставку')
def get_order_delivery(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Оформить')
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Стоимость доставки - 900 руб.', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Оформить')
def confirm_order(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Введите номер вашего заказа:')
    bot.register_next_step_handler(message, confirm_order_step2)


def confirm_order_step2(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Доставка успешно оформлена. Заказ привезут с 11:00-16:00',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Забрать частичный комплект вещей')
def get_partial_order(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Вернуться на главную')
    bot.send_message(message.chat.id, 'Вы можете вернуть свои вещи, если срок аренды не истек')
    bot.send_message(message.chat.id, 'Введите номер вашего заказа:', reply_markup=markup)
    bot.register_next_step_handler(message, show_qr_code)


def show_qr_code(message):
    order_id = int(message.text)
    order = Order.objects.get(pk=order_id)
    img = qrcode.make(str(order.pk))
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    bot.send_photo(message.chat.id, buffer.getvalue())
    bot.send_message(message.chat.id, "Заказ находится по адресу Херсонская улица 38")


@bot.message_handler(func=lambda message: message.text == 'Вернуться на главную')
def send_back(message):
    send_back_to_main(message)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()