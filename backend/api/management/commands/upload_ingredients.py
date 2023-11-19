import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from tqdm import tqdm

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from json file'

    def handle(self, *args, **options):
        try:
            with open('data/ingredients.json', encoding='utf-8') as file:
                data = json.load(file)
            for ingredient in tqdm(data, colour='green'):
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
            self.stdout.write(
                self.style.SUCCESS('Data was successfully imported'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file}" not found'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f'Ingredients located in {file}'
                                               f'already exist'))
