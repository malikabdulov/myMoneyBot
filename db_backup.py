import os
import time
import schedule
import config


def backup_database():
    DB_HOST = config.database['host']
    DB_USER = config.database['user']
    DB_USER_PASSWORD = config.database['password']
    DB_NAME = config.database['database']
    BACKUP_PATH = config.database['backup_path']
    MYSQL_PATH = config.database['mysql_path']

    DATETIME = time.strftime('%Y%m%d-%H%M%S')

    dumpcmd = MYSQL_PATH + "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + DB_NAME + " > " + BACKUP_PATH + "/" + DB_NAME + DATETIME + ".sql"
    os.system(dumpcmd)

    print("Your backups have been created in '" + BACKUP_PATH + "' directory")


schedule.every().tuesday.at("23:03").do(backup_database)
while True:
    schedule.run_pending()
    time.sleep(50)
