import vk_api
import datetime

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import acces_token, comunity_token

class BotInterface:

    def __init__(self, token):
        self.bot = vk_api.VkApi(token=token)
        longpoll = VkLongPoll(self.bot)

    def message_send(self, user_id, message, attachment=None):
        self.bot.method('messages.send',
                        {'user_id': user_id,
                         'message': message,
                         'random_id': get_random_id(),
                         'attachment': attachment
                        }
                        )

    def get_search_info(self, user_id):
        parameters = {'acces_tokens': acces_token,
                      'users_id': user_id,
                      'fields': 'bdat,city,sex,relation'
                      }
        try:
            search_info = self.bot.method('users.get', parameters)
        except KeyError:
            self.message_send(user_id, 'Ошибка получения данных о вас')
            return
        for data in search_info:
            bdata = data.get('bdata')
            sex = data.get('sex')
            city = data.get('city')

        return bdata, sex, city

    def find_sex_user(self, user_sex):
        find_sex = 0
        if user_sex == 1:
            find_sex = 2;
            if user_sex == 2:
                find_sex = 1;
            else:
                find_sex = (input('Введите значение пола человека для поиска(1 - женский, 2 - мужской'))
        return find_sex

    def determine_age(self, user_id, bdate):
        year_now = int(datetime.datetime.now().year)
        check_date = bdate.split(',')
        if check_date[-1] > 1923:
            year_bd = int(check_date[-1])
        else:
            self.message_send(user_id, 'Введите год рождения')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    year_bd = int(event.text.lower())

        age = year_now - year_bd
        if age < 18:
            self.message_send(user_id, 'Подождите, пока исполнится 18 лет')
            exit()
        return age

    def range_age(self, user_id, bdate):
        self.message_send(user_id, 'Диапазон поиска по умолчанию +- 5 лет. Если диапозон устраивает, напишите: "да". Для указания своего, напишите "нет"')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'да':
                    age_min = self.determine_age(user_id, bdate) - 5
                    age_max = self.determine_age(user_id, bdate) + 5
                elif event.text.lower() == 'нет':
                    self.message_send(event.user_id, 'Введите минимальный возраст поиска (минимальный возраст - 18 лет)')
                    age_min = int(event.text.lower())
                    if age_min < 18:
                        self.message_send(user_id, 'Недопустимый возраст')
                        exit()
                    self.message_send(event.user_id, 'Введите максимальный возраст поиска')
                    age_max = int(event.text.lower())
                else:
                    self.message_send(event.user_id, 'Неизвестная команда')
        return [age_min, age_max]

    def determine_city(self, user_id, city_search):
        city_sh = city_search
        if len(city_search) == 0:
            self.message_send(event.user_id, 'Введите город для поиска человека')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city_sh = event.text.lower()
                    id_city = self.seach_id_city(user_id, city_sh)
        return id_city

    def seach_id_city(self, user_id, name_city):
        parametr = {'access_token': acces_token,
                    'country_id': 1,
                    'q': f'{name_city}',
                    'need_all': 0,
                    'count': 1000
                    }
        quest = self.bot.method('database.getCities', parametr)
        try:
            list = quest['response']['items']
            for city_number in list:
                searh_city = city_number.get('title')
                if searh_city == name_city:
                    searh_city_id = city_number.get('id')
                    return int(searh_city_id)
        except KeyError:
            self.message_send(user_id, 'Ошибка получения данных о вас')

    def search_param(self, user_id, bdate, sex_users, name_city):
        find_sex = self.find_sex_user(sex_users)
        city_user = self.determine_city(user_id, name_city)
        age_min = self.range_age(user_id, bdate)[0]
        age_max = self.range_age(user_id, bdate)[1]
        return [find_sex, city_user, age_min, age_max]

    def handler(self):
       longpoll = VkLongPoll(self.bot)
       for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.message_send(event.user_id, 'Добрый день!\n'
                                                     'Я могу помочь найти пару для тебя\n'
                                                     'Для общения со мной используй команды:\n'
                                                     'Поиск - начнем поиск пары\n'
                                                     'Далее - просмотр следующего кондидата\n'
                                                     'Стоп - заканчиваем общение с ботом\n'
                                                     'Помощь - подсказка по командам\n')
                elif event.text.lower() == 'поиск':

                    self.message_send(event.user_id, 'пока не умею')
                elif event.text.lower() == 'далее':
                    pass
                else:
                    self.message_send(event.user_id, 'Неизвестная команда.\n'
                                                     'Воспользуйся командой "помощь"\n')

if __name__ == '__main__':
    bot = BotInterface(comunity_token)
    bot.handler()
    bot.search_param()
    find_sex = bot.search_param()[0]
    city_user = bot.search_param()[1]
    age_min = bot.search_param()[2]
    age_max= bot.search_param()[3]




    # citys_id = self.determine_city(user_id, city_search)
    # ages_from = self.range_age(user_id, bdate)[0]
    # ages_to = self.range_age(user_id, bdate)[1]
    # finds_sex = self.find_sex_user(sex_users)
    # media = f'photo49441168_184333266'
    # bot.message_send(21765042, 'фото', attachment=media)

