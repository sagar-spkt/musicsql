from django.core.management.base import BaseCommand
from django.conf import settings
import psycopg2


class Command(BaseCommand):
    help = "Run 'music_schema.sql'"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            cur = settings.DATABASE.cursor()
            cur.execute(open('music_schema.sql', 'r').read())
            settings.DATABASE.commit()
        except psycopg2.Error:
            settings.DATABASE.rollback()
