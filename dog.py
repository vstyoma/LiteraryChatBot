# import requests
#
# query = input("Введите название: ")
# url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
# response = requests.get(url)
#
# if response.status_code == 200:
#     book = response.json()["items"][0]
#     book_id = book["id"]
#     url_end = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
#
#
#     response_end = requests.get(url_end)
#
#     # Проверяем код ответа
#     if response.status_code == 200:
#         # Извлекаем оценку книги из ответа API
#         rating = response.json()["volumeInfo"]["averageRating"]
#         print(f"Оценка книги: {rating}")
#     else:
#         print("Не удалось получить оценку книги")
# else:
#     pass

# import requests
#
# query = input("Введите название: ")
# url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
# response = requests.get(url)
#
# if response.status_code == 200:
#     book = response.json()["items"][0]
#     book_id = book["id"]
#     url_end = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
#
#     response_end = requests.get(url_end)
#
#     if response_end.status_code == 200:
#         volume_info = response_end.json()["volumeInfo"]
#         if "averageRating" in volume_info:
#             rating = volume_info["averageRating"]
#             print(f"Оценка книги: {rating}")
#         else:
#             print("Оценка книги недоступна")
#     else:
#         print("Не удалось получить данные о книге")
# else:
#     print("Не удалось выполнить поиск книги")

import requests


def get_book_info(book_title):
    url_price = f"https://www.googleapis.com/books/v1/volumes?q={book_title}"
    response_price = requests.get(url_price)
    data_price = response_price.json()

    if data_price["totalItems"] == 0:
        return "Книга не найдена"


    buy_link = data_price["items"][0]["saleInfo"].get("listPrice")

    if buy_link:
        return f"\nСсылка на покупку: {buy_link}"
    else:
        return "Ссылка на покупку недоступна для этой книги"

book_title = "1984"
final_get_url = get_book_info(book_title)
print(final_get_url)






