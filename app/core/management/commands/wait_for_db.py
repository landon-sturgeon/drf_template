"""Package containing the commands for ensuring the PostGRESql DB is up."""

import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command for pausing execution until database is available."""

    def handle(self, *args, **options):
        """Run the checks needed to ensure that the postgresql db is up.

        :param args: all positional arguments needed to check the db
        :param options: all additional arguments needed to check the db
        :return:
        """
        self.stdout.write("Waiting for database...")
        db_conn = None

        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available."))
