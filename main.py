import random
import telebot
import cfg
import utils


bot = telebot.TeleBot(cfg.tg_token)
db = utils.SQLighter(cfg.database)
types = db.get_buttons("type")
colors = db.get_buttons("color")
characters = db.get_buttons("character")
answer_list = ["Как тебе", "Может быть", "А что если", "Может он у тебя будет", "А пускай"]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user.id
    name = f"{message.from_user.first_name} {message.from_user.last_name}"
    utils.new_user(user, name)
    txt = f"""Привет {message.from_user.first_name}, я помогу тебе подобрать имя твоему пушистому другу.

Какое имя ты хочешь?"""
    bot.send_message(message.chat.id, txt, reply_markup=start_keyboard())


@bot.message_handler(commands=['random_name'])
def send_random(message):
    conn = utils.SQLighter(cfg.database)
    user = message.from_user.id
    response_list = conn.get_random()
    utils.update_data(user, response_list=response_list)
    txt = f"""Твое случайное имя {random.choice(response_list)}?"""
    bot.send_message(message.chat.id, txt, reply_markup=start_keyboard())


@bot.message_handler(func=lambda message: message.text == "Для кота на латиннице")
def select_male_lat(message):
    user = message.from_user.id
    utils.update_data(user, params={"lang": "lat", "is_male": 1}, filters={"main": "Клички для котов на латиннице"})
    txt = "Есть такие категории"
    bot.send_message(message.chat.id, txt, reply_markup=main_keyboard_lat())


@bot.message_handler(func=lambda message: message.text == "Для кошки на латиннице️️")
def select_female_lat(message):
    user = message.from_user.id
    utils.update_data(user, params={"lang": "lat", "is_male": 0}, filters={"main": "Клички для кошек на латиннице"})
    txt = "Есть такие категории"
    bot.send_message(message.chat.id, txt, reply_markup=main_keyboard_lat())


@bot.message_handler(func=lambda message: message.text == "Для кота на кириллице")
def select_male_cyr(message):
    user = message.from_user.id
    utils.update_data(user, params={"lang": "cyr", "is_male": 1}, filters={"main": "Клички для котов на кирилице"})
    txt = "Есть такие категории"
    bot.send_message(message.chat.id, txt, reply_markup=main_keyboard_cyr())


@bot.message_handler(func=lambda message: message.text == "Для кошки на кириллице")
def select_female_cyr(message):
    user = message.from_user.id
    utils.update_data(user, params={"lang": "cyr", "is_male": 0}, filters={"main": "Клички для кошек на кирилице"})
    txt = "Есть такие категории"
    bot.send_message(message.chat.id, txt, reply_markup=main_keyboard_cyr())


@bot.message_handler(func=lambda message: message.text == "Имя по типу")
def cat_types(message):
    txt = "Какой тип имени ты хочешь"
    bot.send_message(message.chat.id, txt, reply_markup=custom_keyboard(types))


@bot.message_handler(func=lambda message: message.text == "Имя на букву")
def cat_letters(message):
    txt = "На какую букву ты хочешь имя?"
    markup = telebot.types.ReplyKeyboardRemove(selective=True)
    msg = bot.send_message(message.chat.id, txt, reply_markup=markup)
    bot.register_next_step_handler(msg, add_letter)


@bot.message_handler(func=lambda message: message.text == "Имя по окрасу")
def cat_colors(message):
    txt = "Выбери окрас своего питомца"
    bot.send_message(message.chat.id, txt, reply_markup=custom_keyboard(colors))


@bot.message_handler(func=lambda message: message.text == "Имя по характеру")
def cat_characters(message):
    txt = "Выбери характер своего питомца"
    bot.send_message(message.chat.id, txt, reply_markup=custom_keyboard(characters))


@bot.message_handler(func=lambda message: message.text in types)
def add_type(message):
    user = message.from_user.id
    utils.update_data(user, params={"type": f"{message.text}"}, filters={"type": f"{message.text}"})
    send_for_params(message)


def add_letter(message):
    user = message.from_user.id
    params = utils.get_data(user, "params")
    cyr = "абвгдежзийклмнопрстуфхцчшэюя"
    lat = "abcdefghijklmnopqrstuvwxyz"
    bad_letters = "ыьщ"
    if len(message.text) > 1:
        txt = "Мне нужна только одна буква"
        msg = bot.send_message(message.chat.id, txt)
        bot.register_next_step_handler(msg, add_letter)
    else:
        if message.text.lower() in bad_letters:
            txt = "Очень смешно... давай по нормальному"
            msg = bot.send_message(message.chat.id, txt)
            bot.register_next_step_handler(msg, add_letter)
        elif params["lang"] == "cyr" and message.text.lower() not in cyr:
            txt = "Это не русская буква, а ты выбрал кирилицу, не надо так)\nДавай еще раз"
            msg = bot.send_message(message.chat.id, txt)
            bot.register_next_step_handler(msg, add_letter)
        elif params["lang"] == "lat" and message.text.lower() not in lat:
            txt = "Это не латинская буква, а ты выбрал латинницу, не надо так)\nДавай еще раз"
            msg = bot.send_message(message.chat.id, txt)
            bot.register_next_step_handler(msg, add_letter)
        else:
            utils.update_data(user, params={"name": f"{message.text.upper()}"},
                              filters={"name": f"На букву {message.text.upper()}"})
            send_for_params(message)


@bot.message_handler(func=lambda message: message.text in colors)
def add_color(message):
    user = message.from_user.id
    utils.update_data(user, params={"color": f"{message.text}"}, filters={"color": f"{message.text}"})
    send_for_params(message)


@bot.message_handler(func=lambda message: message.text in characters)
def add_character(message):
    user = message.from_user.id
    utils.update_data(user, params={"character": f"{message.text}"}, filters={"character": f"{message.text}"})
    send_for_params(message)


@bot.message_handler(func=lambda message: message.text == "Назад")
def go_back(message):
    user = message.from_user.id
    txt = "Выбери фильтры"
    params = utils.get_data(user, "params")
    if params["lang"] == "cyr":
        bot.send_message(chat_id=message.chat.id, text=txt, reply_markup=main_keyboard_cyr())
    elif params["lang"] == "lat":
        bot.send_message(chat_id=message.chat.id, text=txt, reply_markup=main_keyboard_lat())


def send_for_params(message):
    user = message.from_user.id
    params = utils.get_data(user, "params")
    filters = utils.get_data(user, "filters").values()
    txt_list = ["Посмотрим что у меня для тебя есть", "Дай подумать", "Секундочку", "Уже ищу"]
    markup = telebot.types.ReplyKeyboardRemove(selective=True)
    bot.send_message(message.chat.id, random.choice(txt_list), reply_markup=markup)
    try:
        conn = utils.SQLighter(cfg.database)
        response_list = conn.select_for_params(**params)
        utils.update_data(user, response_list=response_list)
        txt = f"""Фильтры: {", ".join(filters)}
    
{random.choice(answer_list)} '{random.choice(response_list)}'?"""
        bot.send_message(message.chat.id, text=txt, reply_markup=inline_keyboard())
    except IndexError:
        txt = f"""Фильтры: {", ".join(filters)}

С этими фильтрами нет ниодного варианта :(
Попробуй очистить фильтры и начать сначала"""
        keyboard = telebot.types.InlineKeyboardMarkup()
        clear_filter = telebot.types.InlineKeyboardButton(text="Очистить фильтры", callback_data="clear_filter")
        keyboard.add(clear_filter)
        bot.send_message(message.chat.id, text=txt, reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Отдай" and message.from_user.id == 454231990)
def stupid_answer(message):
    txt = f"{utils.get_users_count()}"
    bot.send_message(message.chat.id, txt)


@bot.message_handler(content_types=["text", "audio", "document", "photo", "sticker", "video"])
def stupid_answer(message):
    txt = """Сорри я не умею говорить на отвлеченные темы. Могу только придумывать имена для котов 
Выбери категорию"""
    bot.send_message(message.chat.id, txt, reply_markup=start_keyboard())


@bot.callback_query_handler(func=lambda call: True)
def main_callback_handler(call):
    user = call.from_user.id
    response_list = utils.get_data(user, "response_list")
    filters = utils.get_data(user, "filters").values()
    params = utils.get_data(user, "params")
    if call.data == "repeat":
        try:
            txt = f"""Фильтры: {", ".join(filters)}

{random.choice(answer_list)} '{random.choice(response_list)}'?"""
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                                  reply_markup=inline_keyboard())
        except telebot.apihelper.ApiTelegramException:
            txt = f"Варианты закончились попробуй изменить фильтры"
            keyboard = telebot.types.InlineKeyboardMarkup()
            clear_filter = telebot.types.InlineKeyboardButton(text="Очистить фильтры", callback_data="clear_filter")
            keyboard.add(clear_filter)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                                  reply_markup=keyboard)
    elif call.data == "add_filter":
        txt = "Какой фильтр хочешь добавить"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"{random.choice(response_list)}")
        if params["lang"] == "cyr":
            bot.send_message(chat_id=call.message.chat.id, text=txt, reply_markup=main_keyboard_cyr())
        elif params["lang"] == "lat":
            bot.send_message(chat_id=call.message.chat.id, text=txt, reply_markup=main_keyboard_lat())
    elif call.data == "clear_filter":
        name = f"{call.message.from_user.first_name} {call.message.from_user.last_name}"
        utils.new_user(user, name)
        txt = "Фильтры очищены, попробуй начать с начала"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"{random.choice(response_list)}")
        bot.send_message(chat_id=call.message.chat.id, text=txt, reply_markup=start_keyboard())


def start_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    man_lat = telebot.types.KeyboardButton("Для кота на латиннице")
    woman_lat = telebot.types.KeyboardButton("Для кошки на латиннице️️")
    man_cyr = telebot.types.KeyboardButton("Для кота на кириллице")
    woman_cyr = telebot.types.KeyboardButton("Для кошки на кириллице")
    keyboard.add(man_lat, woman_lat, man_cyr, woman_cyr)
    return keyboard


def main_keyboard_cyr():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    button_types = telebot.types.KeyboardButton("Имя по типу")
    button_letters = telebot.types.KeyboardButton("Имя на букву")
    button_colors = telebot.types.KeyboardButton("Имя по окрасу")
    button_characters = telebot.types.KeyboardButton("Имя по характеру")
    keyboard.add(button_types, button_letters, button_colors, button_characters)
    return keyboard


def main_keyboard_lat():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    button_types = telebot.types.KeyboardButton("Имя по типу")
    button_letters = telebot.types.KeyboardButton("Имя на букву")
    keyboard.add(button_types, button_letters)
    return keyboard


def custom_keyboard(list_of_keys):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=4)
    button_back = telebot.types.KeyboardButton("Назад")
    keyboard.add(*list_of_keys, button_back)
    return keyboard


def inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    repeat_button = telebot.types.InlineKeyboardButton(text="Еще вариант", callback_data="repeat")
    add_filter = telebot.types.InlineKeyboardButton(text="Добавить/Изменить фильтр", callback_data="add_filter")
    clear_filter = telebot.types.InlineKeyboardButton(text="Очистить фильтры", callback_data="clear_filter")
    keyboard.add(repeat_button, add_filter, clear_filter)
    return keyboard


if __name__ == "__main__":
    bot.polling(none_stop=True)
