import requests

import psycopg2

from config import *

import logging

import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

TOKEN = API_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



class Form(StatesGroup):
    book_name = State()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    connect = sqlite3.connect('tg_users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
           id INTEGER,
           fav_1 VARCHAR(150),
           fav_2 VARCHAR(150),
           fav_3 VARCHAR(150)
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

    await message.reply("Привет!🤗 \n\nЯ -  Литературный Ботик!📚 \n\nНиже мой список команд: \n\n/findinfo - поиск информации о ведённой вами книге. \n Скоро...")





@dp.message_handler(commands=['findinfo',])
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



@dp.message_handler(state=Form.book_name)
async def process_name(message: types.Message, state: FSMContext):

    await state.finish()


    url = "https://www.googleapis.com/books/v1/volumes"



    params = {"q": message.text, "maxResults": 1}
    response = requests.get(url, params=params).json()

    for book in response.get('items', []):

        volume = book["volumeInfo"]
        title = volume["title"]

    # Получение автора с установкой значения по умолчанию
        author = volume.get("authors", ["автор неизвестен"])

        published = volume.get("publishedDate", "год издания неизвестен")
        description = volume.get("description", "описание отсутствует")

        finalansw = [
            f"Название: *{title}* \nГод издательства: *{published}* \nАвтор: *{author[0]}* \nОписание: _{description}_"]

        string = ''
        chars_to_remove = ['[', ']', "'"]

        for i in finalansw:
            string += str(i)
            string += ' '

        for char in chars_to_remove:
            string = string.replace(char, '')
        await message.answer(string, parse_mode="Markdown")





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

