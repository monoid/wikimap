from django.core.management.base import BaseCommand
from astromap.models import Point


__author__ = 'ib'


class Command(BaseCommand):
    args = "<point_id>"
    help = u"Delete specified marker by id."

    def handle(self, *args, **options):
        pid = int(args[0])

        Point.objects.filter(pk=pid).delete()

        self.stdout.write('Point deleted...')