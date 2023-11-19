import json

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from tqdm import tqdm

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tags from json file'

    def handle(self, *args, **options):
        try:
            with open('data/tags.json', encoding='utf-8') as file:
                data = json.load(file)
            for tag in tqdm(data, colour='green'):
                Tag.objects.get_or_create(
                    name=tag.get('name'),
                    color=tag.get('color'),
                    slug=tag.get('slug')
                )
            self.stdout.write(
                self.style.SUCCESS('Data was successfully imported'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file}" not found'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f'Tags located in {file}'
                                               f'already exist'))

