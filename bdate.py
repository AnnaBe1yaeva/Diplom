import psycopg2

from psycopg2 import OperationalError

from config import user_bd, password_bd, name_bd, host_bd, port_bd

def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print('Подключение к базе данных прошло успешно')
    except OperationalError as e:
        print('Произошла ошибка подключения')
    return connection

connect = create_connection(name_bd, user_bd, password_bd, host_bd, port_bd)

def create_table_users():
    with connect.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS viewed_users (
	           id serial,
	           vk_id_search serial, PRIMARY KEY, NOT NULL);"""
            )
    print('[INFO] table viewed_users was created' )

def add_users_in_table():
    with connect.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO viewed_users (vk_id_search) VALUES
               ('{vk_id_search}')"""
        )

# def check_user_in_table(id_num):
#     with connect.cursor() as cursor:
#         cursor.execute(
#             """SELECT vk_id_search FROM viewed_users WHERE vk_id_search=%s; """, (id_num)
#         )
#         return cursor.fetchone()