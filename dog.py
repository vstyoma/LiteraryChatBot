import psycopg2
from config import host, user, password, db_name



try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        print(f"Server version: {cursor.fetchone()}")

except Exception as _ex:
    print("Что-то пошло не так.", _ex)
finally:
    if connection:
        connection.close()
        print("PostgreSQL соединение закрыто.")