import time

from django.core.management.base import BaseCommand

from salesagent.orchestration.worker import process_queue


class Command(BaseCommand):
    help = "Process queued inbound messages (M0 subset). Use --once for a single pass."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Process one batch and exit.")
        parser.add_argument("--interval", type=float, default=2.0, help="Seconds between batches.")

    def handle(self, *args, **options):
        if options["once"]:
            self.stdout.write(str(process_queue()))
            return
        while True:
            process_queue()
            time.sleep(options["interval"])
