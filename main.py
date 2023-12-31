# Импорт всех нужных модулей

import requests
import wikipedia
from config import *

import logging

import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Базовая конфигурация (токен и др.)

TOKEN = API_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

command_count = 0


# Создание машины состояния

class Form(StatesGroup):
    book_name = State()
    wiki_name = State()
    delete_name = State()


# Меню


mainmenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainmenu.add("📕Найти книгу").add("🖥Найти страницу на Википедии").add("🎁Корзина").add(
    "✌Удалить из корзины")


# Команда /start, подключение к ДБ и вывод

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

    connect = sqlite3.connect('tg_users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
           id INTEGER,
           fav_1 VARCHAR(800),
           stats INTEGER

       )""")
    connect.commit()

    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
    data = cursor.fetchone()

    if data is None:
        user_id = [message.chat.id]
        cursor.execute("INSERT INTO login_id (id) VALUES (?);", user_id)
        connect.commit()
    else:
        pass

    await message.reply(
        "Привет!🤗 \n\nЯ -  Литературный Ботик!📚 \n\nЧтобы воспользоваться мною, нажмите на появившиеся кнопки!",
        reply_markup=mainmenu)


# Команда "Найти книгу" с машиной состояния и отменой

@dp.message_handler(text='📕Найти книгу')
async def find_information(message: types.Message):

    await Form.book_name.set()
    await message.answer("Введите название книги. Введите /cancel для отмены команды.")


@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Отменено.')


title = ""


# Основная часть команды

@dp.message_handler(state=Form.book_name)
async def process_name(message: types.Message, state: FSMContext):
    global title
    sql_buts = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Добавить в избранное', callback_data='true_add'))

    await state.finish()

    url = "https://www.googleapis.com/books/v1/volumes"

    params = {"q": message.text, "maxResults": 1}
    response = requests.get(url, params=params).json()

    for book in response.get('items', []):

        volume = book["volumeInfo"]
        title = volume["title"]

        author = volume.get("authors", ["автор неизвестен"])

        published = volume.get("publishedDate", "год издания неизвестен")
        description = volume.get("description", "описание отсутствует")

        url_price = f"https://www.googleapis.com/books/v1/volumes?q={message.text}"
        response_price = requests.get(url_price)
        data_price = response_price.json()

        if data_price["totalItems"] == 0:
            return "Книга не найдена"

        buy_link = data_price["items"][0]["saleInfo"].get("buyLink")
        price_get = data_price["items"][0]["saleInfo"].get("listPrice")

        finalansw = []

        if price_get:
            amount = int(price_get['amount'])
            finalansw.append(f"*Название:* *{title}*")

            if published:
                finalansw.append(f"*Год издательства:* _{published}_")

            if author[0] != "автор неизвестен":
                finalansw.append(f"*Автор:* _{author[0]}_")
            finalansw.append(f"*Цена:* _{amount} рублей_")

            if description:
                finalansw.append(f"*Описание:* _{description}_")

            if buy_link:
                finalansw.append(f"*Ссылка на покупку:* *{buy_link}*")
        else:
            finalansw.append(f"*Название:* *{title}*")

            if published:
                finalansw.append(f"*Год издательства:* _{published}_")

            if author[0]:
                finalansw.append(f"*Автор:* _{author[0]}_")

            if description:
                finalansw.append(f"*Описание:* _{description}_")

        response = '\n\n'.join(finalansw)
        await message.answer(response, parse_mode="Markdown", reply_markup=sql_buts)


@dp.callback_query_handler(lambda c: c.data == 'true_add')
async def add_to_cart_handler(callback_query: types.CallbackQuery):
    global title

    message = callback_query.message
    people_id = message.chat.id

    # Добавление название книги в базу данных

    conn = sqlite3.connect('tg_users.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO login_id (id, fav_1) VALUES ({people_id}, '{title}');")

    conn.commit()

    await message.answer("*Книга была добавлена в избранное.*", parse_mode="Markdown")
    await message.delete_reply_markup()


# Команда "Книга на чтение" + работа с ДБ

@dp.message_handler(text=['🎁Корзина'])
async def show_my_books(message: types.Message):


    people_id = message.chat.id

    conn = sqlite3.connect('tg_users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT fav_1 FROM login_id WHERE id = {people_id}")
    results = cursor.fetchall()
    results1 = ""
    for res in results:
        results1 += res[0] + "\n"

    if results:

        response = f"_Ваша книги в корзине:_\n*{results1}*"
    else:
        response = "_Вы еще не добавили ни одной книги в корзину._"

    str_db = ''
    chars_to_remove = ['[', ']', "'", ",", "(", ")"]

    for i in response:
        str_db += str(i)
        str_db += ''

    for char in chars_to_remove:
        str_db = str_db.replace(char, '')

    await message.answer(str_db, parse_mode="Markdown")


@dp.message_handler(text="✌️Удалить из корзины")
async def delete_book(message: types.Message):

    await Form.delete_name.set()
    await message.answer("*Введите название книги для удаления ее из корзины. Введите /cancel для отмены команды.*", parse_mode="Markdown")


@dp.message_handler(state='#', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_deletestate = await state.get_state()
    if current_deletestate is None:
        return

    await state.finish()
    await message.reply('*Отменено.*', parse_mode="Markdown")


@dp.message_handler(state=Form.delete_name)
async def delete_name_from_cart(message: types.Message, state: FSMContext):
    await state.finish()
    people_id = message.chat.id

    conn = sqlite3.connect('tg_users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM login_id WHERE id = {people_id} AND fav_1 = '{message.text}'")
    result = cursor.fetchone()

    if result is None:
        await message.answer("*Книги не существует. Проверьте корректность вашего сообщения*", parse_mode="Markdown")
    else:
        cursor.execute(f"DELETE FROM login_id WHERE id = {people_id} AND fav_1 = '{message.text}'")
        conn.commit()
        await message.answer("*Книга была удалена.*", parse_mode="Markdown")


# Команда "Найти термин / страницу на Wikipedia"

@dp.message_handler(text='🖥Найти страницу на Википедии')
async def find_wiki(message: types.Message):

    await Form.wiki_name.set()
    await message.answer("*Введите какой-либо термин. Введите /cancel для отмены команды.*", parse_mode="Markdown")


@dp.message_handler(state='^', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_wikistate = await state.get_state()
    if current_wikistate is None:
        return

    await state.finish()
    await message.reply('*Отменено.*', parse_mode="Markdown")


@dp.message_handler(state=Form.wiki_name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        await state.finish()

        wikipedia.set_lang("ru")
        wiki_query = wikipedia.summary(message.text)

        await message.answer(f"*Вот что мы нашли*: \n\n_{wiki_query}_", parse_mode="Markdown")

    except wikipedia.exceptions.PageError as e:
        await message.answer("*Такой страницы не существует. Проверьте корректность вашего предложения.*",
                             parse_mode="Markdown")





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

