import configurations as config

import psycopg2


def create_db_connection():
    try:
        connection = psycopg2.connect(**config.database_credentials)
        connection.autocommit = True
        return connection
    except Exception as e:
        print(f"The error '{e}' occurred")


def close_db_connection(cnx, cursor=None):
    if cursor:
        try:
            cursor.close()
        except Exception as e:
            print(f"The error '{e}' occurred")

    try:
        cnx.close()
    except Exception as e:
        print(f"The error '{e}' occurred")


def get_author_id(telegram_id):
    """
    :param telegram_id: {call.message.from_user.id}
    :return: query result
    """
    cnx = create_db_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT id FROM money_bot.users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"def get_author_id:::Error '{e}' occurred")
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
            "INSERT INTO money_bot.users"
            "         (telegram_id,     telegram_username,     first_name,     last_name)"
            "VALUES (%(telegram_id)s, %(telegram_username)s, %(first_name)s, %(last_name)s)"
        )
    else:
        query = (
            "UPDATE money_bot.users SET "
            "telegram_username = %(telegram_username)s,"
            "first_name = %(first_name)s,"
            "last_name = %(last_name)s"
            "WHERE telegram_id = %(telegram_id)s"
        )
    try:
        cursor.execute(query, user_data)
    except Exception as e:
        print(cursor.statement())
        print(f"def update_users:::Error '{e}' occurred")
    finally:
        close_db_connection(cnx, cursor)
    return


def get_categories():
    cnx = create_db_connection()
    cursor = cnx.cursor()
    query = 'SELECT id, name FROM money_bot.categories ORDER by id'
    try:
        cursor.execute(query)
        output = cursor.fetchall()
        return dict(output)
    except Exception as e:
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
        "INSERT INTO money_bot.expenses "
        "         (category_id, author_id, comment, date, amount) "
        "VALUES (%(category_id)s, %(author_id)s, %(comment)s, %(date)s, %(amount)s )"
    )
    try:
        cursor.execute(query, expense_data)
        return True
    except Exception as e:
        print(f"def insert_new_expense:::Error '{e}' occurred")
        return False
    finally:
        close_db_connection(cnx, cursor)


def get_expenses(limit=1000):
    cnx = create_db_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT c.name, e.comment, date(e.date), e.amount "
                       "FROM money_bot.expenses e "
                       "JOIN money_bot.categories c ON c.id = e.category_id "
                       "ORDER BY e.id DESC "
                       f"LIMIT {limit}")
        result = cursor.fetchall()
        return result  # List[tuple()]
    except Exception as e:
        print(f"def get_expenses:::Error '{e}' occurred")
        return None
    finally:
        close_db_connection(cnx, cursor)


def get_limit(category_id):
    cnx = create_db_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT name, credit_limit, credit_limit - "
                       f"coalesce((SELECT SUM(amount) FROM money_bot.expenses WHERE category_id = {category_id} "
                       "AND extract(month from created_at) = extract(month from current_timestamp) "
                       "AND extract(year from created_at) = extract(year from current_timestamp)), 0) "
                       "FROM money_bot.categories "
                       f"WHERE id = {category_id} ")
        result = cursor.fetchone()  # tuple()

        category_name = result[0]
        limit = result[1]
        available_balance = result[2]

        return category_name, limit, available_balance


    except Exception as e:
        print(f"def get_limit:::Error '{e}' occurred")
        return None
    finally:
        close_db_connection(cnx, cursor)


def get_pivot():
    cnx = create_db_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT c.name, c.credit_limit, coalesce(SUM(e.amount), 0), c.credit_limit - coalesce(SUM(e.amount), 0) "
                        "FROM money_bot.categories c "
                        "LEFT JOIN ( "
                        "SELECT amount, category_id FROM money_bot.expenses "
                        "WHERE extract(month from date) = extract(month from current_timestamp) "
                        "AND extract(year from date) = extract(year from current_timestamp) "
                        ") e ON c.id = e.category_id "                        
                        "GROUP BY c.id;")
        result = cursor.fetchall()
        return result  # list[(name of category, limit, sum of amount, available limit)]
    except Exception as e:
        print(f"def get_pivot:::Error '{e}' occurred")
        return None
    finally:
        close_db_connection(cnx, cursor)


if __name__ == '__main__':
    print(create_db_connection())



