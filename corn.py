import vk_api
from config import acces_token
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


    def user_search(self, city_id, age_from, age_to, sex, offset = None):

        try:
            profiles = self.ext_api.method('users.search',
                                           {'city_id': city_id,
                                            'age_from': age_from,
                                            'age_to': age_to,
                                            'sex': sex,
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
                                      'owner_id': user_id
                                      }
                                     )
        try:
            photos = photos['items']
        except KeyError:
            return

        result = []
        for num, photo in enumerate(photos):
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id']
                           }
                          )
            if num == 2:
                break

        return result



if __name__ == '__main__':
    tools = VkTools(acces_token)

    # info = tools.get_profile_info(21765042)
    # if info:
    #     print(tools.get_profile_info(21765042))
    # else:
    #     print('Произошла ошибка')

# profiles = tools.user_search(1, 20, 40, 1)
# print(profiles)

photos = tools.photos_get(49441168)
print(photos)

media = f'photo_49441168_184333266'