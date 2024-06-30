from django.core.management.base import BaseCommand
from core.apps.email.send_email import main


class Command(BaseCommand):
    help = "Запускаем бота"

    def handle(self, *args, **options):
        main()