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

def create_table_users(connect):
    with connect.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS viewed_users (
	           id serial,
	           vk_id_search varchar(30) NOT NULL PRIMARY KEY);"""
            )
    print('[INFO] таблица viewed_users создана' )

def add_users_in_table(connect, vk_id_search):
    with connect.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO viewed_users (vk_id_search) VALUES
               ('{vk_id_search}')"""
        )
    print(f'{vk_id_search} добавлен в таблицу')

def check_user_in_table(connect, id_number):
    with connect.cursor() as cur:
        cur.execute(
            """SELECT vk_id_search 
            FROM viewed_users 
            WHERE vk_id_search= %s; """, (id_number,)
        )
        return cur.fetchone()

create_table_users(connect)