import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import database as sql
import config
import re
import functions_tg as tfunc
from datetime import date, timedelta

bot = telebot.TeleBot(token=config.potatobot['token'], parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def start_message(message):
    first_name = message.from_user.first_name
    text = f'Привет, *{first_name}*!\nДобро пожаловать! Я бот-помошник!\n\n_Используй команду /help_'
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text=text)
    sql.update_users(message=message)


@bot.message_handler(commands=['help'])
def start_message(message):
    key_new_expense = InlineKeyboardButton(text='Новый расход', callback_data='newExpense')
    key_last_expenses = InlineKeyboardButton(text='Последние 5 расходов', callback_data='lastExpenses')
    markup_inline = InlineKeyboardMarkup()
    markup_inline.add(key_new_expense, key_last_expenses)
    text = f'Доступны команды:\n/start\n/help\n/available\n\nМожно написать:\nостаток\navailable'
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup_inline)


@bot.message_handler(
    func=lambda message: message.text.lower() == '/available' or
                         message.text.lower() == 'available' or
                         message.text.lower() == 'остаток')
def hi_message(message):
    chat_id = message.chat.id
    pivot = sql.get_pivot()
    text = ''
    for line in pivot:  # tuple (name of category, limit, sum of costs, available limit)
        name = line[0]
        available = line[3]
        if available > 0:
            status = 'осталось'
        else:
            status = '*перелимит*'
        text += f'{name} - {status} {available} тенге\n'
    bot.send_message(chat_id=chat_id, text=text)


@bot.callback_query_handler(func=lambda call: True)
def answer_to_call(call):
    print('Callback:', call.data)
    callback = call.data
    chat_id = call.message.chat.id
    msg_id = call.message.id
    src_text = call.message.text
    if callback == 'newExpense':
        text = 'Выбери категорию:'
        categories = sql.get_categories()
        markup_inline = InlineKeyboardMarkup()
        keys = []
        for ID, Name in categories.items():
            keys.append(InlineKeyboardButton(text=f'{Name}', callback_data=f'newExpense{ID}'))
        for i in range(0, len(keys) - 1, 2):
            markup_inline.add(keys[i], keys[i + 1])
        if len(keys) % 2 != 0:
            markup_inline.add(keys[-1])
        markup_inline.add(InlineKeyboardButton(text='Вернуться назад', callback_data='help'))
        bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text=text, reply_markup=markup_inline)
    elif callback == 'lastExpenses':
        text = ''
        expenses = sql.get_expenses(5)
        for expense in expenses:  # tuple (name, comment, date, cost)
            text += f'*{expense[2]}* _{expense[0]}_ - {expense[1]} - {expense[3]} тенге\n'
        key_new_expense = InlineKeyboardButton(text='Новый расход', callback_data='newExpense', )
        key_last_expenses = InlineKeyboardButton(text='Последние 5 расходов', callback_data='lastExpenses')
        markup_inline = InlineKeyboardMarkup()
        markup_inline.add(key_new_expense, key_last_expenses)
        bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text=text, reply_markup=markup_inline)
    elif callback == 'help':
        key_new_expense = InlineKeyboardButton(text='Новый расход', callback_data='newExpense', )
        key_last_expenses = InlineKeyboardButton(text='Последние 5 расходов', callback_data='lastExpenses')
        markup_inline = InlineKeyboardMarkup()
        markup_inline.add(key_new_expense, key_last_expenses)

        text = f'You can use buttons bellow.'
        bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text=text, reply_markup=markup_inline)
    elif re.match(pattern='newExpense\d+', string=callback):
        category_id = re.findall(pattern='\d+', string=callback)
        telegram_id = call.from_user.id
        expense = {'category_id': int(category_id[0]),
                   'telegram_id': int(telegram_id)}

        today = str(date.today())
        yesterday = str(date.today() - timedelta(days=1))
        two_days_ago = str(date.today() - timedelta(days=2))
        three_days_ago = str(date.today() - timedelta(days=3))

        key_today = InlineKeyboardButton(text=today)
        key_yesterday = InlineKeyboardButton(text=yesterday)
        key_two_days_ago = InlineKeyboardButton(text=two_days_ago)
        key_three_days_ago = InlineKeyboardButton(text=three_days_ago)

        markup_inline = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup_inline.add(key_today, key_yesterday)
        markup_inline.add(key_two_days_ago, key_three_days_ago)

        category_name, limit, available_balance = sql.get_limit(expense['category_id'])

        text1 = f'*{category_name}*\nЛимит - {limit}\nДоступная сумма - {available_balance}'
        text2 = 'Введи дату расхода.\nПример: *2020-12-21*'
        bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text=text1)
        msg = bot.send_message(chat_id=chat_id, text=text2, reply_markup=markup_inline)
        bot.register_next_step_handler(msg, get_expense_comment, expense)


def get_expense_comment(message, expense):
    expense['date'] = message.text
    chat_id = message.chat.id
    text = 'Введи комментарий к расходу'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_expense_cost, expense)


def get_expense_cost(message, expense):
    expense['comment'] = message.text
    chat_id = message.chat.id
    text = 'Введи стоимость\n\n_Важно!: только целое число_'
    msg = bot.send_message(chat_id=chat_id, text=text)
    bot.register_next_step_handler(msg, new_expense, expense)


def new_expense(message, expense):
    chat_id = message.chat.id
    input = message.text
    if input.isdigit():
        expense['cost'] = int(input)
        result = sql.insert_new_expense(expense)
        if result:
            text = 'Новый расход успешно сохранен!'
        else:
            text = 'Новый расход *не сохранен*, зови Малика!'
        bot.send_message(chat_id=chat_id, text=text)
    else:
        text = 'Нужно целое число. Введи еще раз.'
        msg = bot.send_message(chat_id=chat_id, text=text)
        bot.register_next_step_handler(msg, new_expense, expense)


if __name__ == '__main__':
    print('Bot is running')
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print('Occurred:', e)
