import os
import time
import schedule
import configurations as config


def backup_database():
    DB_HOST = config.database_credentials['host']
    DB_USER = config.database_credentials['user']
    DB_USER_PASSWORD = config.database_credentials['password']
    DB_NAME = config.database_credentials['database']
    BACKUP_PATH = config.backup['backup_path']
    MYSQL_PATH = config.backup['mysql_path']

    DATETIME = time.strftime('%Y%m%d-%H%M%S')

    dumpcmd = MYSQL_PATH + "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + DB_NAME + " > " + BACKUP_PATH + "/" + DB_NAME + DATETIME + ".sql"
    os.system(dumpcmd)

    print("Your backups have been created in '" + BACKUP_PATH + "' directory")


schedule.every().friday.at("23:02").do(backup_database)
while True:
    schedule.run_pending()
    time.sleep(1)
