import requests
query = input()












url = "https://www.googleapis.com/books/v1/volumes"

params = {"q": query, "maxResults": 1}
response = requests.get(url, params=params).json()

for book in response.get('items', []):

    volume = book["volumeInfo"]
    title = volume["title"]

    # Получение автора с установкой значения по умолчанию
    author = volume.get("authors", ["--"])

    published = volume.get("publishedDate", "год издания неизвестен")
    description = volume.get("description", "описание отсутствует")

    finalansw = [
        f"Название: {title} \nГод издательства: {published} \nАвтор: {author[0]} \nОписание: {description}"]

    string = ''
    chars_to_remove = ['[', ']', "'"]

    for i in finalansw:
        string += str(i)
        string += ' '

    for char in chars_to_remove:
        string = string.replace(char, '')
    print(string)





