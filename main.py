import vk_api
import datetime

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import acces_token, comunity_token
from bdate import check_user_in_table, add_users_in_table, connect

from operator import itemgetter
from vk_api.exceptions import ApiError

class BotFunction:

    def __init__(self):
        self.bot = vk_api.VkApi(token=comunity_token)
        self.ext_api = vk_api.VkApi(token=acces_token)
        self.longpoll = VkLongPoll(self.bot)

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
                      'user_ids': user_id,
                      'fields': 'bdate,city,sex'
                      }
        try:
            search_info = self.bot.method('users.get', parameters)
        except KeyError:
            self.message_send(user_id, 'Ошибка получения данных о вас')
            return
        for data in search_info:
            name_user = data.get('first_name')
            bdate = data.get('bdate')
            sex = data.get('sex')
            city_us = data.get('city')

        return  name_user, bdate, sex, city_us

    def find_sex_user(self, user_sex):
        find_sex = 0
        if user_sex == 1:
            find_sex = 2;
            if user_sex == 2:
                find_sex = 1;
        return find_sex

    def range_age(self, age_min, age_max):
        if age_min.isdigit == True and age_max.isdigit == True:
            age_min_sh = int(age_min)
            age_max_sh = int(age_max)
        else:
            age_min_sh = 0
            age_max_sh = 0
            if age_min_sh < 18:
                age_min_sh = 0
        return [age_min_sh, age_max_sh]


    def get_city(self, ids, messages):
        self.message_send(ids, messages)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    request = str(event.text)

                except:
                    self.message_send(ids, "Введи город верно")
                else:
                    return request

    def seach_id_city(self, name_city):
        parametr = {'access_token': acces_token,
                    'country_id': 1,
                    'q': f'{name_city}',
                    'need_all': 0,
                    'count': 1000
                    }
        quest = self.ext_api.method('database.getCities', parametr)
        list = quest['items']

        try:
            for city_number in range(len(list)):
                list_city = list[city_number]
                look_city = list_city.get('title')
                if look_city == name_city:
                    searh_city_id = list_city.get('id')
                    return int(searh_city_id)
        except KeyError:
            self.message_send(user_id, 'Ошибка получения данных')

    def get_profile_info(self, user_id):

        try:
            info = self.ext_api.method('users.get',
                                        {'user_id': user_id,
                                         'fields': 'bdat,city,sex,relation'}
                                       )
        except ApiError:
            return

        return info

    def user_search(self, city_id, age_from, age_to, sex, status, offset = None):

        try:
            profiles = self.ext_api.method('users.search',
                                           {'city_id': city_id,
                                            'age_from': age_from,
                                            'age_to': age_to,
                                            'sex': sex,
                                            'status': status,
                                            'count': 30,
                                            'offset': offset
                                            }
                                           )
        except ApiError:
            return

        profiles = profiles['items']

        result = []
        for profile in profiles:
            if profile['is_closed'] == False:
                result.append({'name': profile['first_name']+ ' ' + profile['last_name'],
                              'id': profile['id']
                              })
        return result

    def photos_get(self, user_id):
        photos = self.ext_api.method('photos.get',
                                     {'album_id': 'profile',
                                      'owner_id': user_id,
                                      'extended': 1,
                                      'photo_sizes': 1,
                                      'count': 1000
                                      }
                                     )
        try:
            photos = photos['items']
        except KeyError:
            return

        result = []
        for num, photo in enumerate(photos):
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id'],
                           'likes': photo['likes']['count']
                          }
                          )
        sorted_result = sorted(result, key=itemgetter('likes'), reverse = True)
        top3_photo = sorted_result[0:3]

        return top3_photo

    def get_age(self, ids, messages):
        self.message_send(ids, messages)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    request = int(event.text)
                except:
                    self.message_send(ids, "Введи возраст цифрами")
                else:
                    return request


if __name__ == '__main__':
    bot = BotFunction()

    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            info = bot.get_search_info(event.user_id)
            user_id = event.user_id
            # print(info)
            us_name = info[0]
            us_bdate = info[1]

            if event.text.lower() == 'привет':
                bot.message_send(event.user_id, f'Добрый день, {us_name} \n'
                                                    'Я могу помочь найти пару для тебя\n'
                                                    'Для общения со мной используй команды:\n'
                                                    'Поиск - определение параметров поиска\n'
                                                    'Далее - просмотр возможных кондидатов\n'
                                                    'Стоп - заканчиваем общение с ботом\n'
                                                    'Помощь - подсказка по командам\n')
            elif event.text.lower() == 'поиск':
                bot.message_send(event.user_id, 'Давай определим параметры поиска')
                seeker_sex = bot.find_sex_user(info[2])
                city_searh = info[3]['id']
                counter = 1
                offset_check = 1
                bot.message_send(event.user_id, f'Город для поиска по умолчанию - ваш город в профиле\n'
                                                 'Если хотите указать другой город или в профиле не указан, напишите "город"\n')
                year_now = int(datetime.datetime.now().year)
                check_date = us_bdate.split('.')
                year_bd = int(check_date[-1])
                if year_bd > 1923:
                    seeker_bdate = year_bd
                else:
                    year_bd <= 1923
                    bot.message_send(event.user_id, f'Для запуска поиска необходимо верно указать свой год рождения в профиле\n'
                                                        'Вам должно быть больше 18 лет\n')
                age = year_now - seeker_bdate
                if age < 18:
                    bot.message_send(event.user_id, 'Подождите, пока исполнится 18 лет')
                    exit()
                bot.message_send(event.user_id, f'Диапазон поиска по умолчанию +\-5 лет\n'
                                                'Для подбора кандидата наберите: Далее\n')
                age_min_search = age - 5
                if age_min_search < 18:
                    age_min_search = 18
                age_max_search = age + 5

                bot.message_send(event.user_id, f'Если хотите указать свой диапазон\n'
                                                 'для указания минимального возраста, напишите "мин"\n'
                                                 'для указания максимального возраста, напишите "макс"\n')

            elif event.text.lower() == 'мин':
                age_min_search = bot.get_age(event.user_id, f'минимальный возраст (цифрами):\n')
                if age_min_search < 18:
                    bot.message_send(event.user_id, 'Недопустимый возраст, поиск происходит от 18 лет\n'
                                                    'для введения корректного возраста, напишите "мин"\n')
                print(age_min_search)
                bot.message_send(event.user_id, f'для указания максимального возраста, напишите "макс"\n'
                                                 'для поиска с максимальным возрастом +5лет, напишите "далее"\n')


            elif event.text.lower() == 'макс':
                age_max_search = bot.get_age(event.user_id, f'максимальный возраст (цифрами):\n')
                print(age_max_search)
                if age_min_search > age_max_search:
                    bot.message_send(event.user_id, 'Некорректно введен возрастной диапазон, начните сначала: "поиск"\n')
                else:
                    bot.message_send(event.user_id, 'Для продолжения работы, напишите "далее"\n')

            elif event.text.lower() == 'город':
                city_s = bot.get_city(event.user_id, f'Город для поиска:\n')
                city_searh = bot.seach_id_city(city_s)
                bot.message_send(event.user_id, 'Для продолжения работы, напишите "мин" для указания возрастных диапазонов\n'
                                                'Или "далее" для продолжения поиска с возрастным диапазоном по умолчанию\n')
                offset_check = 1
            elif event.text.lower() == 'далее':
                city_searh_id = city_searh

                list = bot.user_search(city_searh_id, age_min_search, age_max_search, seeker_sex, 6, offset_check)
                quantity = range(len(list))
                print(list)
                while counter != quantity:
                    name_sh = list[counter-1]['name']
                    id_sh = list[counter-1]['id']
                    if not check_user_in_table(connect, str(id_sh)):
                        bot.message_send(event.user_id, f'Имя найденного человека {name_sh}\n'
                                                        f'vk.com/id{id_sh}')
                        media_photo = bot.photos_get(id_sh)
                        for i in range(len(media_photo)):
                            owner = media_photo[i]['owner_id']
                            id_us = media_photo[i]['id']
                            media = f'photo{owner}_{id_us}'
                            bot.message_send(event.user_id, 'фото', attachment=media)
                        add_users_in_table(connect, id_sh)
                        bot.message_send(event.user_id, 'Если хочешь продолжить поиск, набери "Далее')
                        break
                    else:
                        counter += 1
                offset_check += 10

                if event.text.lower() == 'далее':
                    counter +=1

            elif event.text.lower() == 'помощь':
                bot.message_send(event.user_id, 'Для общения со мной используй команды:\n'
                                                'Поиск - определение параметров поиска\n'
                                                'Далее - просмотр возможных кондидатов\n'
                                                'Стоп - заканчиваем общение с ботом\n'
                                                'Помощь - подсказка по командам\n')

            elif event.text.lower() == 'стоп':
                bot.message_send(event.user_id, 'До новых встреч!')
                exit()
            else:
                bot.message_send(event.user_id, 'Неизвестная команда.\n'
                                                'Воспользуйся командой "помощь"\n')

