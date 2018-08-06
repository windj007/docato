import json, base64, traceback, os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User


class Command(BaseCommand):
    args = ''
    help = 'Ensure that superuser exists and assigned desired password'

    option_list = BaseCommand.option_list + (
        make_option('--pwd',
                    type = str,
                    default = 'adminpwd',
                    help = 'Password to set'),
        make_option('--force',
                    action = 'store_true',
                    help = 'Whether to update password if admin user exists'),
    )

    def handle(self, *args, **options):
        admin = User.objects.filter(username='admin').first()
        if admin is not None:
            if options.get('force', False):
                admin.set_password(options['pwd'])
        else:
            User.objects.create_superuser('admin', 'admin@example.com', options['pwd'])
