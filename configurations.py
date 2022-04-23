import os

env = 'heroku' if os.environ.get('DATABASE_URL') else 'local'

if env == 'heroku':
    from urllib.parse import urlparse

    result = urlparse(os.environ.get('DATABASE_URL'))
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    database_credentials = {
        'user': username,
        'password': password,
        'host': hostname,
        'dbname': database,
        'port': port
    }

    potato_bot = {
        'name': 'PotatoNotesBOt',
        'mobile_number': '+77017970774',
        'token': '1197564328:AAFtGfbhfOSMa3dryImoG_Uxtqzf27N5a9Q'
    }
else:
    database_credentials = {
        'user': 'postgres',
        'password': 'root',
        'host': 'localhost',
        'dbname': 'postgres',
        'port': 5433
    }

    potato_bot = {
        'name': '@testpotatoobot',
        'mobile_number': '+77017970774',
        'token': '1271380641:AAGIknz1H1i0GDDfdAZi5jhKCcey5Zx2zU0'
    }

# backup = {
#     'backup_path': 'C:\OpenServer\mysqlbackups',
#     'mysql_path': 'C:\OpenServer\modules\database\MySQL-8.0\\bin\\',
# }
