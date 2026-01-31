#!/usr/bin/env python
import os
import sys
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from django.core.management import execute_from_command_line
    from django.contrib.auth.models import User
    from api.models import InstituteDomain
    import hashlib

    if len(sys.argv) < 2:
        print('Usage: python manage_setup.py [command]')
        print('Commands:')
        print('  init-db          - Run migrations')
        print('  create-admin     - Create admin user')
        print('  seed-domains     - Add common institute domains')
        print('  seed-stickers    - Add default stickers')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'init-db':
        print('Running migrations...')
        execute_from_command_line(['manage.py', 'migrate'])
        print('Database initialized.')

    elif command == 'create-admin':
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD_HASH')

        if not admin_password:
            print('Error: ADMIN_PASSWORD_HASH not set')
            sys.exit(1)

        if User.objects.filter(username=admin_email).exists():
            print(f'Admin user {admin_email} already exists.')
        else:
            admin = User.objects.create_superuser(admin_email, admin_email, admin_password)
            print(f'Admin user created: {admin_email}')

    elif command == 'seed-domains':
        domains = [
            'iit.ac.in',
            'iitmandi.ac.in',
            'iitbhu.ac.in',
            'iitd.ac.in',
            'iitg.ac.in',
            'iitkgp.ac.in',
            'iitr.ac.in',
            'iitm.ac.in',
            'iitb.ac.in',
            'du.ac.in',
            'delhi.ac.in',
            'jnu.ac.in',
            'nus.edu.sg',
            'stanford.edu',
            'berkeley.edu',
            'mit.edu',
        ]

        for domain in domains:
            obj, created = InstituteDomain.objects.get_or_create(
                domain=domain,
                defaults={'verified': True}
            )
            if created:
                print(f'Added domain: {domain}')
            else:
                print(f'Domain already exists: {domain}')

    elif command == 'seed-stickers':
        from api.models import Sticker

        sticker_packs = {
            'Smileys': [
                {'name': 'Happy', 'image_url': '/stickers/happy.png'},
                {'name': 'Sad', 'image_url': '/stickers/sad.png'},
                {'name': 'Love', 'image_url': '/stickers/love.png'},
            ],
            'Reactions': [
                {'name': 'Thumbs Up', 'image_url': '/stickers/thumbs-up.png'},
                {'name': 'Fire', 'image_url': '/stickers/fire.png'},
                {'name': 'Clap', 'image_url': '/stickers/clap.png'},
            ],
        }

        for pack_name, stickers in sticker_packs.items():
            for sticker_data in stickers:
                obj, created = Sticker.objects.get_or_create(
                    name=sticker_data['name'],
                    pack_name=pack_name,
                    defaults={
                        'image_url': sticker_data['image_url'],
                        'premium': False,
                        'token_cost': 0,
                    }
                )
                if created:
                    print(f'Added sticker: {pack_name}/{sticker_data["name"]}')

    print('Done.')
