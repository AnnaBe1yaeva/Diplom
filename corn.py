import vk_api
from config import acces_token
from dip import find_sex, city_user, age_min, age_max
from operator import itemgetter
from vk_api.exceptions import ApiError


class VkTools():
    def __init__(self, token):
        self.ext_api = vk_api.VkApi(token=token)

    def get_profile_info(self, user_id):

        try:
            info = self.ext_api.method('users.get',
                                        {'user_id': user_id,
                                         'fields': 'bdat,city,sex,relation'}
                                       )
        except ApiError:
            return

        return info

    def user_search(self, city_id, age_from, age_to, sex, relation, offset = None):

        try:
            profiles = self.ext_api.method('users.search',
                                           {'city_id': city_id,
                                            'age_from': age_from,
                                            'age_to': age_to,
                                            'sex': sex,
                                            'relation': relation,
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
        sorted_result = sorted(result, key=itemgetter(2), reverse = True)
        top3_photo = sorted_result[0:3]

        return top3_photo


if __name__ == '__main__':
    tools = VkTools(acces_token)

    # info = tools.get_profile_info(21765042)
    # if info:
    #     print(tools.get_profile_info(21765042))
    # else:
    #     print('Произошла ошибка')

# profiles = tools.user_search(citys_id, ages_from, ages_to, finds_sex, 6, 30)
# print(profiles)

    # photos = tools.photos_get(49441168)
    # print(photos)

media = f'photo_49441168_184333266'