import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from json file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            with open(options.get('file'), encoding='utf-8') as file:
                data = json.load(file)
            for ingredient in data:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file}" not found'))
        self.stdout.write(self.style.SUCCESS('Data was successfully imported'))
