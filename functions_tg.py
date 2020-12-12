import database
from main import bot, InlineKeyboardMarkup, InlineKeyboardButton


def note_registration(message):
    title = message.text
    busy = database.is_title_exists(title)
    if not busy:

        insert_result = database.insert_new_note(title)

        if insert_result:
            msg = 'Congratulation! You are Note "%s" successfully added!' % title
        else:
            msg = 'Sorry, something went wrong :('
    else:
        msg = 'A note with the same title already exists!'

    bot.send_message(message.chat.id, msg)


def edit_title_name(message, callback, prev_message_id):
    title = message.text
    busy = database.is_title_exists(title)

    if not busy:
        update_result = database.update_note_title(title, callback)

        if update_result:
            msg = 'Congratulation\! Title *"%s"* successfully updated\!' % title
            print(msg)
        else:
            msg = 'Sorry, something went wrong :('

    else:
        msg = 'A note with the same title already exists!'

    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=prev_message_id,
                          text=msg,
                          parse_mode='MarkdownV2')

    # Construct message with inline keyboard like a call callback_data of some note

    note_title = database.get_note_title(callback)

    key_edit_title = InlineKeyboardButton(text='Edit title', callback_data=f'edit-title-{callback}')
    key_edit_content = InlineKeyboardButton(text='Edit content', callback_data=f'edit-content-{callback}')
    key_delete_note = InlineKeyboardButton(text='Delete Note', callback_data=f'delete-{callback}')
    key_back_notes_list = InlineKeyboardButton(text='Back to notes list', callback_data='notes_list')

    markup_inline = InlineKeyboardMarkup()
    markup_inline.add(key_edit_title, key_edit_content, key_delete_note)
    markup_inline.add(key_back_notes_list)

    bot.send_message(chat_id=message.chat.id,
                     text=f'What do you want to do with "*{note_title}*"?',
                     reply_markup=markup_inline,
                     parse_mode='MarkdownV2')


def add_new_content(message, callback, message_id):
    content = message.text

    is_note_exists = database.is_callback_exists(callback)

    if is_note_exists:
        update_result = database.insert_new_content(content, callback)

        if update_result:
            msg = 'Congratulation! New row added!🎉🎉🎉'
        else:
            msg = 'Sorry, something went wrong :('
    else:
        msg = "A note doesn't exists!"

    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message_id,
                          text=msg)

    content_list = database.get_note_content(callback)

    key_add_row = InlineKeyboardButton(text='Add row', callback_data=f'add-row-{callback}')
    key_edit_row = InlineKeyboardButton(text='Edit row', callback_data=f'show-row-{callback}')

    markup_inline = InlineKeyboardMarkup()
    markup_inline.add(key_add_row, key_edit_row)

    msg = '\n'.join(content_list)

    bot.send_message(text=msg, chat_id=message.chat.id,
                     reply_markup=markup_inline)
