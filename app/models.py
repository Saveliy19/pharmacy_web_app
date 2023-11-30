from werkzeug.security import generate_password_hash, check_password_hash

from app.routes import session

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import app
from app import login

from flask_login import UserMixin

class Database(object):



    @classmethod
    def _connect_to_db(cls) -> psycopg2:
        try:
            # Подключение к существующей базе данных
            cls._connection = psycopg2.connect(user='gosha',
                                        password="gosha",
                                        host='localhost',
                                        database='aptekaru')

        #обработка ошибок при подключении
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'other error:\n{ex}')
        else:
            print("Успешное подключение к БД\n")
        return cls._connection
    
    # метод для обработки запросов на добавление-обновление-удаление данных
    @classmethod
    def execute_query(cls, query) -> bool:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Запрос выполнен успешно!\n')
            return True
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто\n")
        return False

    # метод обработки селект-запросов
    @classmethod
    def select_query(cls, query) -> list:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Вот результат селекта:\n')
            print(result)
            return result
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто\n")
        return None

    @classmethod
    def insert_returning(cls, query: str) -> object:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the insert returning query is successfully')
            return result
        return None

class Client(UserMixin):


    def __init__(self,
                id: int = 0,
                email: str = "",
                password_hash: str="",
                name: str = ""):

                self.id : int = id
                self.email: str = email
                self.password_hash: str = password_hash
                self.name : str = name
                self.role = "client"

    def __repr__(self):
        return f'<User {self.email}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.email}'
        return string

    #добавляем пользователя
    def adduser(self):
        query = f'''INSERT INTO CLIENT (EMAIL, PASSWORD, NAME) 
                    VALUES ('{self.email}', '{self.password_hash}', '{self.name}');'''
        return Database.execute_query(query)

    # генерация хэш-пароля
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        print("Пароль для пользователя успешно сгенерирован")
        print(self.password_hash)

    # проверка хэша
    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

         #получаем пользователя по id
    def get_by_id(id: int):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM CLIENT WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print(f"Пользователь с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Client(* params)

    #получаем айди клиента по его мылу
    def get_id_by_email(email):
        query = f'''SELECT ID FROM CLIENT WHERE EMAIL = '{email}';'''
        result = Database.select_query(query)
        return result[0][0]

        #получаем пользователя по почте
    def get_by_email(email: str):
        query = f'''SELECT * FROM CLIENT WHERE EMAIL = '{email}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Client(* params)


class Administrator(UserMixin):


    def __init__(self,
                id: int = 0,
                username: str = "",
                password_hash: str = "",
                name: str = "",
                market_id: int = 0):

                self.id : int = id
                self.username: str = username
                self.password_hash: str = password_hash
                self.name : str = name
                self.market_id: int = market_id
                self.role = "admin"

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.username}'
        return string

     # проверка пароля
    def check_password(self, password: str):
        if self.password_hash == password:
            return True
        return False


     #получаем админа по id
    def get_by_id(id: int):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM ADMIN WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print(f"Пользователь с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Administrator(* params)

    #получаем админа по логинку
    def get_by_username(username: str):
        query = f'''SELECT * FROM ADMIN WHERE USERNAME = '{username}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Administrator(* params)


class Market():
    #получаем информацию об аптеке по айди
    def get_info_by_id(id):
        query = f'''SELECT ADRES, START_TIME, END_TIME
                    FROM MARKET WHERE ID='{id}';'''
        result = Database.select_query(query)
        return result


    #список всех аптек
    def get_list():
        query = f'''SELECT ID, ADRES
                    FROM MARKET;'''
        result = Database.select_query(query)
        return result

    #получаем айди аптеки по ее адресу
    def get_id_by_adres(adres):
        query = f'''SELECT ID FROM MARKET WHERE ADRES = '{adres}';'''
        result = Database.select_query(query)
        return result[0][0]

    #добавляем новый товар в аптеку
    def add_new_product(market_id, product_id):
        query = f'''INSERT INTO MEDICAMENT_IN_MARKET (MARKET_ID, MEDICAMENT_ID)
                    VALUES('{market_id}', '{product_id}');'''
        return Database.execute_query(query)


    #получаем аптеку в которой работает админ
    def get_by_admin_username(username):
        query = f'''SELECT ADRES, START_TIME, END_TIME
                    FROM MARKET JOIN ADMIN
                    ON MARKET.ID = ADMIN.MARKET_ID
                    WHERE ADMIN.USERNAME = '{username}';'''
        result = Database.select_query(query)
        return result

    #обновляем режим работы
    def update_working_time_by_adres(adres, start_time, end_time):
        query = f'''UPDATE MARKET
                    SET START_TIME = '{start_time}', END_TIME = '{end_time}'
                    WHERE ADRES = '{adres}';'''
        return Database.execute_query(query)


class Medicament():
    #ищем те продукты, которых нет в этой аптеке
    def get_missing_in_market(adres):
        query = f'''SELECT MEDICAMENT.ID, MEDICAMENT.NAME
                    FROM MEDICAMENT
                    WHERE MEDICAMENT.ID NOT IN
                    (SELECT MEDICAMENT_ID FROM MEDICAMENT_IN_MARKET
                    JOIN MARKET ON MARKET.ID = MEDICAMENT_IN_MARKET.MARKET_ID
                    WHERE MARKET.ADRES = '{adres}');'''
        result = Database.select_query(query)
        return result

    #обновляем размер скидки
    def update_sale(medicament_id, sale):
        query = f'''UPDATE MEDICAMENT
                    SET SALE = '{sale}'
                    WHERE ID = '{medicament_id}';'''
        return Database.execute_query(query)

    #Обновляем стоимость товара
    def update_cost(medicament_id, cost):
        query = f'''UPDATE MEDICAMENT
                    SET COST = '{cost}'
                    WHERE ID = '{medicament_id}';'''
        return Database.execute_query(query)

    #получаем список товаров в аптеке
    def get_list_by_market_adres(adres):
        query = f'''SELECT MEDICAMENT.ID, MEDICAMENT.NAME, MEDICAMENT.COST, MEDICAMENT.SALE
                    FROM MEDICAMENT JOIN MEDICAMENT_IN_MARKET
                    ON MEDICAMENT.ID = MEDICAMENT_IN_MARKET.MEDICAMENT_ID
                    JOIN MARKET ON MARKET.ID = MEDICAMENT_IN_MARKET.MARKET_ID
                    WHERE MARKET.ADRES = '{adres}';'''
        result = Database.select_query(query)
        return result

    #получаем список продуктов по запросу из поисковой строки
    def get_list_by_search(search):
        query = f'''SELECT ID, NAME, SALE, TYPE FROM MEDICAMENT WHERE lower(NAME) LIKE '%{search}%';'''
        result = Database.select_query(query)
        return result

    #получаем список всей продукции из базы данных
    def get_types():
        query = f'''SELECT TYPE FROM MEDICAMENT'''
        result = Database.select_query(query)
        return result

    #получаем список товаров в этой категории
    def get_list_by_type(type, search):
        query = f'''SELECT ID, NAME, SALE, TYPE FROM MEDICAMENT WHERE TYPE='{type}' AND lower(NAME) LIKE '%{search}%';'''
        result = Database.select_query(query)
        return result

    
    #получаем информацию о продукте по его айди
    def get_information_by_id(id):
        query = f'''SELECT * FROM MEDICAMENT WHERE ID = '{id}';'''
        result = Database.select_query(query)
        return result

    #получаем список товаров по акции
    def get_sale(search):
        query = f'''SELECT ID, NAME, SALE, TYPE FROM MEDICAMENT WHERE SALE > 0 AND lower(NAME) LIKE '%{search}%';'''
        result = Database.select_query(query)
        return result

    #получаем список аптек, где есть этот товар
    def get_market_by_id(id):
        query = f'''SELECT MARKET.ID, ADRES 
                    FROM MARKET JOIN MEDICAMENT_IN_MARKET
                    ON MARKET.ID = MEDICAMENT_IN_MARKET.MARKET_ID
                    WHERE MEDICAMENT_ID = '{id}';'''
        result = Database.select_query(query)
        return result

#корзина
class Cart():

    #создаем новую корзину пользователю
    def add(user_id, user_email):
        query = f'''INSERT INTO CART (CLIENT_ID, CLIENT_EMAIL) VALUES ('{user_id}', '{user_email}');'''
        return Database.execute_query(query)

    #получаем последнюю корзину юзера по его мылу
    def get_by_email(email):
        query = f'''SELECT ID FROM CART WHERE CLIENT_EMAIL='{email}' 
        AND ID IN (SELECT MAX(ID) FROM CART WHERE CLIENT_EMAIL='{email}');'''
        result = Database.select_query(query)
        return result[0][0]

class Position():
    #добавление позиции к корзине
    def add(cart_id, product_id, count):
        query = f'''INSERT INTO POSITION(CART_ID, PRODUCT_ID, COUNT)
                    VALUES ('{cart_id}', '{product_id}', '{count}');'''
        return Database.execute_query(query)

    #список позиций в корзине по имейлу
    def get_cart_by_user(email):
        query = f'''SELECT MEDICAMENT.NAME, MEDICAMENT.COST, POSITION.COUNT, MEDICAMENT.SALE
                    FROM MEDICAMENT JOIN POSITION 
                    ON MEDICAMENT.ID = POSITION.PRODUCT_ID
                    JOIN CART
                    ON CART.ID = POSITION.CART_ID
                    JOIN CLIENT ON CART.CLIENT_ID=CLIENT.ID
                    WHERE POSITION.OFFER_ID IS NULL AND CLIENT.EMAIL='{email}';'''
        result = Database.select_query(query)
        return result

    #получаем количество товаров и стоимость по каждой отдельной позиции
    def get_summ_by_user(email):
        query = f'''SELECT COST, COUNT FROM POSITION JOIN CART
        ON POSITION.CART_ID=CART.ID
        JOIN MEDICAMENT ON MEDICAMENT.ID=POSITION.PRODUCT_ID
        WHERE CART.CLIENT_EMAIL='{email}' AND POSITION.OFFER_ID IS NULL;'''
        result = Database.select_query(query)
        return result

class Offer():
    #установка срока хранения 
    def set_holding_date(offer_id, date):
        query = f'''UPDATE OFFER
                    SET HOLDING_LAST_DATE='{date}'
                    WHERE ID='{offer_id}';'''
        return Database.execute_query(query)

    #обновление статуса заказа
    def update_status(status, offer_id):
        query = f'''UPDATE OFFER
                    SET STATUS = '{status}'
                    WHERE ID = '{offer_id}';'''
        return Database.execute_query(query)

    #список товаров идущих в эту аптеку
    def get_uncomplited_by_admin(taking_type, adress):
        query = f'''SELECT ID FROM OFFER
                    WHERE TAKING_TYPE = '{taking_type}' AND RECEIVING_ADRES = '{adress}';'''
        result = Database.select_query(query)
        return result

    #получаем список товаров в заказе
    def get_products_list_by_id(id):
        query = f'''SELECT MEDICAMENT.NAME, MEDICAMENT.COST, POSITION.COUNT, MEDICAMENT.SALE
                    FROM POSITION JOIN MEDICAMENT
                    ON MEDICAMENT.ID = POSITION.PRODUCT_ID
                    WHERE OFFER_ID = '{id}';'''
        result = Database.select_query(query)
        return result

    #получаем информацию о заказе
    def get_info_by_id(id):
        query = f'''SELECT to_char(OFFER_DATE, 'dd-mm-YYYY'), to_char(COMPLITE_DATE, 'dd-mm-YYYY'), STATUS, TAKING_TYPE, PAY_TYPE, to_char(HOLDING_LAST_DATE, 'dd-mm-YYYY'), RECEIVING_ADRES, COST
                    FROM OFFER WHERE ID='{id}';'''
        result = Database.select_query(query)
        return result

    #создаем заказ
    def add(offer_date, taking_type, pay_type, adress, cart_id, cost):
        query = f'''INSERT INTO OFFER(OFFER_DATE, COMPLITE_DATE, STATUS, TAKING_TYPE, PAY_TYPE, RECEIVING_ADRES, CART_ID, COST)
        VALUES('{offer_date}', '{offer_date}', 'В сборке', '{taking_type}', '{pay_type}', '{adress}', '{cart_id}', '{cost}') returning ID;'''
        result =  Database.insert_returning(query)
        return result[0]


    def set_offer(offer_id, email):
        query = f'''UPDATE POSITION
                SET OFFER_ID='{offer_id}'
                WHERE OFFER_ID IS NULL AND CART_ID IN (SELECT ID FROM CART JOIN POSITION ON CART.ID=POSITION.CART_ID WHERE CLIENT_EMAIL='{email}');'''
        return Database.execute_query(query)

    #список неполученных клиентом заказов
    def get_uncomplited_by_email(email):
        query = f'''SELECT OFFER.ID FROM OFFER JOIN CART
                    ON OFFER.CART_ID = CART.ID
                    JOIN CLIENT
                    ON CLIENT.ID = CART.CLIENT_ID
                    WHERE (STATUS = 'В сборке' OR STATUS = 'Доставляется' OR STATUS = 'Ожидает в аптеке')
                    AND CLIENT.EMAIL = '{email}';'''
        result = Database.select_query(query)
        return result

    #получаем список по типу доставки
    def get_by_taking_type(taking_type):
        query = f'''SELECT ID FROM OFFER WHERE TAKING_TYPE = '{taking_type}'
                    AND (STATUS = 'В сборке' OR STATUS = 'Доставляется');'''
        result = Database.select_query(query)
        return result

    #список полученных клиентом заказов
    def get_complited_by_email(email):
        query = f'''SELECT OFFER.ID FROM OFFER JOIN CART
                    ON OFFER.CART_ID = CART.ID
                    JOIN CLIENT
                    ON CLIENT.ID = CART.CLIENT_ID
                    WHERE (STATUS = 'Получен клиентом')
                    AND CLIENT.EMAIL = '{email}';'''
        result = Database.select_query(query)
        return result

#метод загрузки клиента:
@login.user_loader
def load_user(id: str):
    if session['role'] == 'admin':
        user = Administrator.get_by_id(int(id))
    elif session['role'] == 'client':
        user = Client.get_by_id(int(id))
    print(f'user loaded, user = {user}')
    return user

     