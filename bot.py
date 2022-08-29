import telebot
import mysql.connector
import re

bot = telebot.TeleBot('YOUR-TOKEN')

db = mysql.connector.connect(
    host='localhost',
    user='USER',
    passwd='PASSWORD',
    port='3306',
    database='beer_bot'
)

cursor = db.cursor()

# cursor.execute('CREATE DATABASE beer_bot')

# cursor.execute('SELECT * FROM users WHERE user_id = ')
# for x in cursor:
#     print(x)

# cursor.execute('CREATE TABLE users (name VARCHAR(255), beer_count FLOAT)')
# cursor.execute('ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)')

# sql = 'INSERT INTO users(name, beer_count, user_id) VALUES (%s, %s, %s)'
# val = ('Алексей', 2, 12355)
# cursor.execute(sql, val)
# db.commit()

user_data = {}


class User:
    def __init__(self, beer):
        self.beer = beer


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """A function that registers new users to the database and welcomes those already registered"""

    cursor.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
    res = cursor.fetchone()
    if res:
        bot.reply_to(message, f'Ооо, это опять ты, {message.from_user.first_name}. '
                              f'Можешь посмотреть мой список команд с помощью /help')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAECF_pgWe3vqeYPCuhEDaPXW31xu-StngACzwEAAladvQrnnqjJFNimhR4E')
    else:
        bot.reply_to(message, f'Меня зовут C-3PO. Я твой пивной бот, {message.from_user.first_name}. '
                              f'Можешь посмотреть список команд с помощью /help')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAECF_pgWe3vqeYPCuhEDaPXW31xu-StngACzwEAAladvQrnnqjJFNimhR4E')
        user_id = message.from_user.id
        sql = 'INSERT INTO users(name, beer_count, user_id) VALUES (%s, %s, %s)'
        val = (message.from_user.first_name, 0, user_id)
        cursor.execute(sql, val)
        db.commit()


@bot.message_handler(commands=['help'])
def send_help(message):
    """The function processes the help command"""

    bot.send_message(chat_id=message.from_user.id,
                     text='Это бот для подсчета выпитого пива. Нажми /beer и отправь число.'
                          ' Если случайно ввёл больше, не беда, просто напиши сколько хочешь отнять со знаком "-". '
                          'Команда /total покажет сколько ты выпил, а /statistic сравнение с другими пользователями')


@bot.message_handler(commands=['beer'])
def beer_question(message):
    """The function processes the beer command. Runs a function beer_count"""

    bot.send_message(chat_id=message.from_user.id, text='И сколько же пива ты выпил?')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAECF_hgWe3kVW2aG5NHagABo7mah9KSW-UAAiUBAAKZmEYR9xUPPRbgR9AeBA')
    bot.register_next_step_handler(message, beer_count)


def beer_count(message):
    """The function updates the database with the number entered by the user."""

    responses = {'/start': send_welcome, '/help': send_help,
                 '/total': beer_result, '/beer': beer_question}
    user_id = message.from_user.id
    if message.text in responses.keys():
        responses[message.text](message)
    else:
        parseNumber(message.text)
        try:
            if flag:
                user = User(beer_value)
                sql = f'UPDATE users SET beer_count=beer_count+{user.beer} WHERE user_id={user_id}'
                cursor.execute(sql)
                db.commit()
                if user.beer == '0':
                    bot.send_sticker(message.chat.id,
                                     'CAACAgIAAxkBAAECF_xgWe-jNFoYgS0ZTdjNApTGqFygowACgAADiTlSDeDkumqx9L5aHgQ')
                elif user.beer[0] == '-':
                    bot.send_message(chat_id=message.from_user.id, text=f'Я отнял {user.beer} от твоего пива')
                else:
                    bot.send_message(chat_id=message.from_user.id, text='Данные успешно добавлены!')
            else:
                bot.send_message(chat_id=message.from_user.id, text='Мне нужны цифры, Лебовски')
                beer_question(message)
        except:
            bot.send_message(chat_id=message.from_user.id, text='Что-то пошло не так(((')


@bot.message_handler(commands=['total'])
def beer_result(message):
    """The function processes the total command. Prints total value of beer"""

    cursor.execute(f'SELECT beer_count FROM users WHERE user_id={message.from_user.id}')
    res = cursor.fetchone()
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAECGAJgWfJWnrcCEC3tvdG4MZDABniDPwACHgIAAviIow0CCdz9119R3B4E')
    bot.send_message(chat_id=message.from_user.id, text=f'Тобой выпито уже {round(res[0], 2)} литров')


@bot.message_handler(commands=['statistic'])
def send_statistic(message):
    """The function processes the statistics command.
    Compares the value of the user in the database, with the global value"""

    count = 0
    cursor.execute('SELECT beer_count FROM users')
    global_result = cursor.fetchall()
    cursor.execute(f'SELECT beer_count FROM users WHERE user_id={message.from_user.id}')
    single_result = cursor.fetchone()
    for k in global_result:
        for i in k:
            if single_result[0] > i:
                count += 1
    x = count / len(global_result) * 100

    bot.send_message(chat_id=message.from_user.id, text=f'Ты выпил больше чем {round(x, 2)}% пользователей')


def parseNumber(text):
    """function checks the number for correctness"""

    global beer_value
    global flag
    flag = False
    text = text.replace(',', '.')
    if re.match(r'^-?\d+$|^-?\d+\.?\d+$', text):
        flag = True
    beer_value = text
    print(type(beer_value))


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)
