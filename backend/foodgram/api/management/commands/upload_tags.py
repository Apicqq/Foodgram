import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tags from json file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            with open(options.get('file'), encoding='utf-8') as file:
                data = json.load(file)
            for tag in data:
                Tag.objects.get_or_create(
                    name=tag.get('name'),
                    color=tag.get('color'),
                    slug=tag.get('slug')
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file}" not found'))
        self.stdout.write(self.style.SUCCESS('Data was successfully imported'))
