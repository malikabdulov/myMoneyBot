from builtins import type
import config
import mysql.connector
from mysql.connector import Error


def create_db_connection():
    connection = mysql.connector.connect(**config.database)

    try:
        connection = mysql.connector.connect(**config.database)
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def close_db_connection(cnx, cursor=None):
    if cursor:
        try:
            cursor.close()
        except Error as e:
            print(f"The error '{e}' occurred")

    try:
        cnx.close()
    except Error as e:
        print(f"The error '{e}' occurred")


def get_author_id(telegram_id):
    """
    :param telegram_id: {call.message.from_user.id}
    :return: query result
    """
    cnx = create_db_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"def username_is_exist:::Error '{e}' occurred")
        return None
    finally:
        close_db_connection(cnx, cursor)


def update_users(message):
    cnx = create_db_connection()
    cursor = cnx.cursor()
    user_data = {
        'telegram_id': message.from_user.id,
        'telegram_username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    exist = get_author_id(user_data['telegram_id'])

    if not exist:
        query = (
            "INSERT INTO users"
            "         (telegram_id,     telegram_username,     first_name,     last_name)"
            "VALUES (%(telegram_id)s, %(telegram_username)s, %(first_name)s, %(last_name)s)"
        )
    else:
        query = (
            "UPDATE users SET "
            "telegram_username = %(telegram_username)s,"
            "first_name = %(first_name)s,"
            "last_name = %(last_name)s"
            "WHERE telegram_id = %(telegram_id)s"
        )
    try:
        cursor.execute(query, user_data)
    except Error as e:
        print(cursor.statement())
        print(f"def update_users:::Error '{e}' occurred")
    finally:
        close_db_connection(cnx, cursor)
    return


def get_categories():
    cnx = create_db_connection()
    cursor = cnx.cursor()
    query = 'SELECT id, name FROM categories ORDER by id'
    try:
        cursor.execute(query)
        output = cursor.fetchall()
        return dict(output)
    except Error as e:
        print(f"def get_categories:::Error '{e}' occurred")
        return False
    finally:
        close_db_connection(cnx, cursor)


def insert_new_expense(expense_data: dict):
    cnx = create_db_connection()
    cursor = cnx.cursor()

    author_id = get_author_id(expense_data['telegram_id'])[0]
    expense_data['author_id'] = author_id
    query = (
        "INSERT INTO expenses "
        "         (category_id, author_id, comment, date, cost) "
        "VALUES (%(category_id)s, %(author_id)s, %(comment)s, %(date)s, %(cost)s )"
    )
    try:
        cursor.execute(query, expense_data)
    except Error as e:
        print(f"def insert_new_expense:::Error '{e}' occurred")
    finally:
        close_db_connection(cnx, cursor)


def get_expenses(limit=1000):
    cnx = create_db_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT c.name, e.comment, date(e.date), e.cost "
                       "FROM expenses e "
                       "JOIN categories c ON c.id = e.category_id "
                       f"LIMIT {limit}")
        result = cursor.fetchall()
        return result  # List[tuple()]
    except Error as e:
        print(f"def get_expenses:::Error '{e}' occurred")
        return None
    finally:
        close_db_connection(cnx, cursor)

#     return
#
#
#
#
# def is_title_exists(note_title):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "SELECT title FROM notes WHERE title = %s"
#
#     try:
#         cursor.execute(query, (note_title,))
#         if cursor.fetchone():
#             return True
#         else:
#             return False
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def insert_new_note(title):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "INSERT INTO notes (title) VALUES ( %s )"
#     try:
#         cursor.execute(query, (title,))
#         return True
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def insert_new_content(content, callback):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "INSERT INTO note_contents (note_id, content) " \
#             "VALUES (" \
#             "(SELECT id FROM notes WHERE callback_data = %s), %s)"
#     try:
#         cursor.execute(query, (callback, content))
#         print('[SQL] Statement: ', cursor.statement)
#         return True
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def update_note_title(title, callback):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "UPDATE notes SET title = %s WHERE  callback_data = %s;"
#     try:
#         cursor.execute(query, (title, callback))
#         return True
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def get_notes_list():
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "SELECT callback_data, title FROM notes"
#     cursor.execute(query)
#
#     output = cursor.fetchall()
#     output = dict(output)
#
#     close_db_connection(cnx, cursor)
#
#     # return dict={callback_data : title} or None
#     return output
#
#
# def get_note_title(callback_data):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "SELECT title FROM notes WHERE callback_data = %s"
#     cursor.execute(query, (callback_data,))
#     output = '%s' % cursor.fetchone()
#
#     close_db_connection(cnx, cursor)
#     # Return str
#     return output
#
#
# def remove_note(callback):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "DELETE FROM notes WHERE callback_data = %s"
#
#     try:
#         cursor.execute(query, (callback,))
#         return True
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def is_callback_exists(callback):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "SELECT callback_data FROM notes WHERE callback_data = %s"
#
#     try:
#         cursor.execute(query, (callback,))
#         if cursor.fetchone():
#             return True
#         else:
#             return False
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def get_contents_list(callback):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "SELECT nc.content_callback, nc.content " \
#             "FROM notes n " \
#             "JOIN note_contents nc ON n.id = nc.note_id " \
#             "WHERE n.callback_data = %s"
#
#     try:
#         cursor.execute(query, (callback,))
#         output = cursor.fetchall()
#         output = dict(output)
#
#         return output  # return dict={content_callback : content} or None
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)
#
#
# def get_content_callback(content_callback):
#     cnx = create_db_connection()
#     cursor = cnx.cursor()
#
#     query = "SELECT content_callback, content " \
#             "FROM note_contents " \
#             "WHERE content_callback = %s"
#
#     try:
#         cursor.execute(query, (content_callback,))
#         output = cursor.fetchall()
#         output = dict(output)
#
#         return output  # return dict={content_callback : content} or None
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return False
#     finally:
#         close_db_connection(cnx, cursor)


if __name__ == '__main__':
    res = get_expenses()
    for r in res:
        print(r[2])



