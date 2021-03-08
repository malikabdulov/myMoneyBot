import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import database as sql
import config
import re
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
def help_message(message, callback=False):
    key_new_expense = InlineKeyboardButton(text='Новый расход', callback_data='newExpense')
    key_last_expenses = InlineKeyboardButton(text='Последние 5 расходов', callback_data='lastExpenses')
    key_limits = InlineKeyboardButton(text='Доступные суммы', callback_data='limits')
    markup_inline = InlineKeyboardMarkup()
    markup_inline.add(key_new_expense, key_last_expenses)
    markup_inline.add(key_limits)
    text = f'Доступны команды:\n/start\n/help\n/available\n\nМожно написать:\nостаток\navailable'
    chat_id = message.chat.id
    if callback:
        bot.edit_message_text(message_id=message.id, chat_id=chat_id, text=text, reply_markup=markup_inline)
    else:
        bot.send_message(chat_id=chat_id, text=text, reply_markup=markup_inline)


@bot.message_handler(func=lambda message: message.text.lower() in ['/available', 'available', 'остаток'])
def limits_message(message, callback=False):
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
    if callback:
        key_help = InlineKeyboardButton(text='Вернуться назад', callback_data='help')
        markup_inline = InlineKeyboardMarkup()
        markup_inline.add(key_help)
        bot.edit_message_text(message_id=message.id, chat_id=message.chat.id, text=text, reply_markup=markup_inline)
    else:
        bot.send_message(chat_id=chat_id, text=text)


@bot.message_handler(func=lambda message: message.text.lower() in ['/newexpense', 'новый расход'])
def newExpense_message(message, callback=False):
    text = 'Выбери категорию:'
    chat_id = message.chat.id
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
    if callback:
        bot.edit_message_text(message_id=message.id, chat_id=chat_id, text=text, reply_markup=markup_inline)
    else:
        bot.send_message(chat_id=chat_id, text=text, reply_markup=markup_inline)


@bot.message_handler(func=lambda message: message.text.lower() in ['/lastexpenses', 'последние расходы'])
def lastExpenses_message(message, callback=False):
    text = ''
    expenses = sql.get_expenses(5)
    chat_id = message.chat.id
    for expense in expenses:  # tuple (name, comment, date, cost)
        text += f'*{expense[2]}* _{expense[0]}_ - {expense[1]} - {expense[3]} тенге\n'
    if callback:
        key_help = InlineKeyboardButton(text='Вернуться назад', callback_data='help')
        markup_inline = InlineKeyboardMarkup()
        markup_inline.add(key_help)
        bot.edit_message_text(message_id=message.id, chat_id=chat_id, text=text, reply_markup=markup_inline)
    else:
        bot.send_message(chat_id=chat_id, text=text)


@bot.callback_query_handler(func=lambda call: True)
def answer_to_call(call):
    print('Callback:', call.data)
    callback = call.data
    chat_id = call.message.chat.id
    msg_id = call.message.id
    src_text = call.message.text
    if callback == 'newExpense':
        newExpense_message(call.message, True)
    elif callback == 'limits':
        limits_message(call.message, True)
    elif callback == 'lastExpenses':
        lastExpenses_message(call.message, True)
    elif callback == 'help':
        help_message(call.message, True)
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
        text2 = 'Введи дату расхода.\nПример: *2021-03-23*'
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
        key_new_expense = InlineKeyboardButton(text='Новый расход', callback_data='newExpense')
        markup_inline = InlineKeyboardMarkup()
        markup_inline.add(key_new_expense)
        bot.send_message(chat_id=chat_id, text=text, reply_markup=markup_inline)
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
