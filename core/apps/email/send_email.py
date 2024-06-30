import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.apps.bot.models import Order
from datetime import datetime
from datetime import timedelta
from environs import Env


env = Env()
env.read_env()
outgoing_email = env.str('EMAIL')
smtp_port = env.int('SMTP_PORT')
password = env.str('EMAIL_PASSWORD')
server_address = env.str('SERVER_ADDRESS')


def send_message(email, messag):
    msg = MIMEMultipart()
    msg['From'] = outgoing_email
    msg['To'] = email
    msg['Subject'] = 'Напоминание'
    message = f'Срок хранения истекает через {messag}'
    msg.attach(MIMEText(message))
    try:
        mailserver = smtplib.SMTP(server_address, smtp_port)
        mailserver.set_debuglevel(True)
        # Определяем, поддерживает ли сервер TLS
        mailserver.ehlo()
        # Защищаем соединение с помощью шифрования tls
        mailserver.starttls()
        # Повторно идентифицируем себя как зашифрованное соединение перед аутентификацией.
        mailserver.ehlo()
        mailserver.login(outgoing_email, password)
        mailserver.sendmail(outgoing_email, email, msg.as_string())
        mailserver.quit()
        print("Письмо успешно отправлено")
    except smtplib.SMTPException:
        print("Ошибка: Невозможно отправить сообщение")


def scan_dates():
    while True:
        orders = Order.objects.all()
        for order in orders:
            current_date = datetime.now()
            format_current_date = current_date.strftime("%m/%d/%Y %H:%M:%S")
            format_current_date_f = datetime.strptime(format_current_date, '%m/%d/%Y %H:%M:%S')
            end_date_f = datetime.strptime(order.end_date, '%m/%d/%Y %H:%M:%S')
            if end_date_f - format_current_date_f == timedelta(minutes=3):
                message = '1 месяц'
                send_message(order.email, message)
            elif end_date_f - format_current_date_f == timedelta(minutes=2):
                message = '2 недели'
                send_message(order.email, message)
            elif end_date_f - format_current_date_f == timedelta(minutes=1):
                message = '3 дня'
                send_message(order.email, message)


def main():
    scan_dates()


if __name__ == "__main__":
    main()

