import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import json
import time
import datetime
from bot_token import TOKEN


bot = telebot.TeleBot(token=TOKEN)
ADMIN_CHAT_ID = 813541786

markup3 = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
yes_ans = KeyboardButton(text="Да.")
no_ans = KeyboardButton(text="Нет.")
markup3.add(yes_ans, no_ans)

markup4 = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
cancel_ans = KeyboardButton(text="Отмена.")
markup4.add(cancel_ans)


def last_message():
    return str(datetime.datetime.now().time())[:5:]


@bot.message_handler(commands=['start'])
def start(m):
    user_id = m.from_user.id
    username = m.from_user.username

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
    edit_checklist_button = KeyboardButton(text="/editchecklist")
    set_reminder_button = KeyboardButton(text="/setreminder")
    tickout_button = KeyboardButton(text="/tickout")
    report_button = KeyboardButton(text="/report")

    if user_id == ADMIN_CHAT_ID:
        warn_button = KeyboardButton(text='/warn')
        markup.add(edit_checklist_button, set_reminder_button, tickout_button, report_button, warn_button)
    else:
        markup.add(edit_checklist_button, set_reminder_button, tickout_button, report_button)

    with open('users.json', 'r') as f:
        users_data = json.load(f)

    if str(user_id) not in users_data:
        users_data[user_id] = {"username": username, "checklist": [], "reminds": {}, "last_msg": str(last_message())}
        bot.send_message(m.chat.id, f'{username}, вы зарегистрированы!', reply_markup=markup)
        with open('users.json', 'w') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
    else:
        bot.send_message(m.chat.id, 'Вы в меню.', reply_markup=markup)


def wait_for_answer_edit_checklist(m: Message):
    b = m.text
    if b == 'Да.':
        bot.send_message(m.chat.id, 'Отправьте мне список ваших дел, разделенных запятыми с пробелами.')
        bot.register_next_step_handler(m, handler_edit_checklist)
    else:
        start(m)

# В РАЗРАБОТКЕ!!!
# def wait_for_answer_waiter(m: Message):
#     if m.text == 'Нет.':
#         pass
#
#
# def answer_waiter(m, t):
#     time.sleep(10)
#     bot.send_message(m.chat.id, 'Уже готово?', reply_markup=markup3)
#
#     bot.register_next_step_handler(m, wait_for_answer_waiter)
#     with open('users.json', 'r') as f:
#         users_data = json.load(f)
#     del users_data[str(m.from_user.id)]['reminds'][t]
#     with open('users.json', 'w') as f2:
#         json.dump(users_data, f2, indent=4, ensure_ascii=False)


def waiter(t, d, m):
    print(t, d)
    while True:
        with open('users.json', 'r') as f:
            users_data = json.load(f)
        if users_data[str(m.from_user.id)]['reminds'][t]:
            now_time = str(datetime.datetime.now().time())[:5:]
            print(now_time)
            if now_time >= t:
                print(2)
                bot.send_message(m.chat.id, f'Пора {d.lower()}!')
                del users_data[str(m.from_user.id)]['reminds'][t]
                break
        with open('users.json', 'w') as f2:
            json.dump(users_data, f2, indent=4, ensure_ascii=False)
        time.sleep(60)


def handler_edit_checklist(m: Message):
    a = m.text.split(', ')
    print(a)
    with open('users.json') as f:
        user_data = json.load(f)

    user_id = m.from_user.id
    user_data[str(user_id)]["checklist"] = a
    with open('users.json', 'w') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)
    bot.reply_to(message=m, text='Записал. Желаю успехов в ваших делах!')
    start(m)


def set_reminder_waiter(m: Message):
    if m.text == 'Отмена.':
        start(m)
    else:
        a, b = m.text.split(' - ')
        print(a)

        bot.send_message(m.chat.id, 'Отлично! Я запомнил.')
        with open('users.json') as f:
            user_data = json.load(f)

        user_id = m.from_user.id
        user_data[str(user_id)]["reminds"][b] = a

        with open('users.json', 'w') as f:
            json.dump(user_data, f, indent=4, ensure_ascii=False)
        waiter(b, a, m)


def check_reminder(m, last_message_time):
    print(1)
    last_time_to_minutes = int(last_message_time[:2:]) * 60 + int(last_message_time[3::])
    while True:
        now_time_to_minutes = int(last_message()[:2:]) * 60 + int(last_message()[3::])
        print(last_time_to_minutes, now_time_to_minutes)
        if now_time_to_minutes - last_time_to_minutes == 3600:
            bot.send_message(m.chat.id, 'Вы не отмечали список около часа. Пора взяться за дела!')
        time.sleep(1800)


@bot.message_handler(commands=['editchecklist'])
def edit_checklist(m):
    with open('users.json') as f:
        user_data = json.load(f)

    user_id = str(m.from_user.id)
    user_data[user_id]["last_msg"] = last_message()
    if user_data[str(user_id)]["checklist"]:
        markup2 = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        yes_button = KeyboardButton(text="Да.")
        cancel_button = KeyboardButton(text="Отмена.")
        markup2.add(yes_button, cancel_button)

        temp = 'У вас уже есть список:\n'
        for i in user_data[str(user_id)]["checklist"]:
            temp += i + '\n'
        temp += '\nХотите его редактировать?'
        bot.send_message(m.chat.id, temp, reply_markup=markup2)
        bot.register_next_step_handler(m, wait_for_answer_edit_checklist)
    else:
        bot.send_message(m.chat.id, 'Отправьте мне список ваших дел, разделенных запятыми с пробелами.')
        bot.register_next_step_handler(m, handler_edit_checklist)

    with open('users.json', 'w') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)

    if user_data[str(user_id)]["checklist"] and (9 <= datetime.datetime.now().hour <= 23):
        check_reminder(m, user_data[user_id]["last_msg"])


@bot.message_handler(commands=['setreminder'])
def set_reminder(m):
    bot.send_message(m.chat.id, 'Напишите, о чем и когда вам нужно напомнить в виде: "Порадоваться жизни - 22:00" '
                                '(без кавычек)', reply_markup=markup4)
    bot.register_next_step_handler(m, set_reminder_waiter)


def waiter_tickout(m: Message):
    a = m.text.split(', ')
    if a[0] == 'Отмена.':
        start(m)
        return

    with open('users.json') as f:
        user_data = json.load(f)

    for i in a:
        user_data[str(m.from_user.id)]["checklist"].remove(i)

    bot.send_message(m.chat.id, 'Вычеркнул!')
    user_data[str(m.from_user.id)]["last_msg"] = last_message()

    with open('users.json', 'w') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)
    start(m)


@bot.message_handler(commands=['tickout'])
def tickout(m):
    with open('users.json') as f:
        user_data = json.load(f)

    temp = f'Какое дело из списка вы хотите вычеркнуть? ' \
           f'Если дел несколько, напишите их через запятую и пробел. \n\nВаш список: \n'
    for i in user_data[str(m.from_user.id)]["checklist"]:
        temp += i + '\n'
    bot.send_message(m.chat.id, temp, reply_markup=markup4)
    bot.register_next_step_handler(m, waiter_tickout)


def report_waiter(m):
    if m.text == 'Отмена.':
        start(m)
    else:
        bot.send_message(ADMIN_CHAT_ID, f'Письмо от пользователя '
                                        f'@{m.from_user.username}:\n{m.text.lower()}')


@bot.message_handler(commands=['report'])
def report(m: Message):
    bot.send_message(m.chat.id, f'{m.from_user.username}, о чем бы хотели связаться с админом? '
                                f'Это письмо придет ему лично: пишите, как будто обращаетесь к нему.'
                                f'\n\nПри необходимости админ ответит вам лично', reply_markup=markup4)
    bot.register_next_step_handler(m, report_waiter)


def warn_waiter(m):
    if m.text == 'Отмена.':
        start(m)

    else:
        a, b = m.text.split(': ')
        with open('users.json') as f:
            user_data = json.load(f)
        for i in user_data:
            # print(a, user_data[i]["username"])
            if a == user_data[i]["username"]:
                bot.send_message(i, f'От админа: {b.lower()}')
        start(m)


@bot.message_handler(commands=['warn'])
def warn(m: Message):
    if 9 <= datetime.datetime.now().hour <= 23:
        if m.from_user.id != ADMIN_CHAT_ID:
            bot.send_message(m.chat.id, 'Недостаточно прав.')

        else:
            bot.send_message(m.chat.id, 'Введите сообщение пользователю с ником '
                                        '"user" в виде: \n"user: message"', reply_markup=markup4)
            bot.register_next_step_handler(m, warn_waiter)
    else:
        bot.send_message(m.chat.id, 'АДМИНЫ ТОЖЕ ХОТЯТ СПАТЬ! Приходите утром:)')
        start(m)


bot.polling()
