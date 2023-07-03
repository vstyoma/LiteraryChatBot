import requests

import logging

from aiogram import Bot, Dispatcher, executor, types


API_TOKEN = '5944894990:AAF1ivQiWLxnRbG6_E0sapKwlUbZwoF78zw'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

    await message.reply("Привет!🤗 \n\nЯ -  Литературный Ботик!📚 \n\nНиже мой список команд: \n\n/findinfo - поиск информации о ведённой вами книге. \n Скоро...")

@dp.message_handler(commands=['findinfo',])
async def find_information(message: types.Message):
     await message.answer("Введите название книги:")

     url = "https://www.googleapis.com/books/v1/volumes"

     query = str(message.text)

     params = {"q": query, "maxResults": 1}
     response = requests.get(url, params=params).json()

     for book in response['items']:


          volume = book["volumeInfo"]
          title = volume["title"]
          author = volume["authors"]

          published = volume.get("publishedDate", "год издания неизвестен")
          description = volume.get("description", "описание отсутствует")

# url = "https://www.googleapis.com/books/v1/volumes"
# query = "1984"
#
# params = {"q": query, "maxResults": 1}
# response = requests.get(url, params=params).json()
#
# for book in response['items']:
#      volume = book["volumeInfo"]
#      title = volume["title"]
#      author = volume["authors"]
#
#      published = volume.get("publishedDate", "год издания неизвестен")
#      description = volume.get("description", "описание отсутствует")
#
#
#
#
#      if author:
#
#           finalansw = [f"**{title}** ({published})| {author} | {description}"]
#
#           string = ''
#           chars_to_remove = ['[', ']', "'"]
#
#           for i in finalansw:
#                string += str(i)
#                string += ' '
#
#           for char in chars_to_remove:
#                string = string.replace(char, '')
#           print(string)
#
#      else:
#           finalansw = [f"**{title}** ({published})| - | {description}"]
#
#           string = ''
#           chars_to_remove = ['[', ']', "'"]
#
#           for i in finalansw:
#                string += str(i)
#                string += ' '
#
#           for char in chars_to_remove:
#                string = string.replace(char, '')
#           print(string)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

