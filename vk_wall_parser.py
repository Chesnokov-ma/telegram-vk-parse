import requests
import json


class VKWallParser:
    """Парсинг сообществ Вконтакте по id или домену. Не работает для парсинга личных страниц по причине другого формата
    ответа от сервера."""

    def __init__(self, vk_token: int, owner_id: int, version: float = 5.92):
        self.__vk_token = vk_token
        self.__owner_id = owner_id
        self.__version = version

    def __parse(self, domains, last_post_was_lst, depth_count=10):
        output_dict = {}
        counter = 0

        for domain in domains:
            by_owner_id = True  # id страницы сообщества
            domain_id = None

            try:
                domain_id = int(domain)  # проверяем указан id или domain
            except TypeError:
                by_owner_id = False
            except ValueError:
                by_owner_id = False

            if by_owner_id:
                response = requests.get('https://api.vk.com/method/wall.get',  # делаем запрос к вк по owner_id
                                        params={
                                            'access_token': self.__vk_token,
                                            'v': self.__version,
                                            'owner_id': -domain_id,
                                            'count': depth_count,
                                        })
            else:
                response = requests.get('https://api.vk.com/method/wall.get',  # делаем запрос к вк по domain
                                        params={
                                            'access_token': self.__vk_token,
                                            'v': self.__version,
                                            'domain': domain,
                                            'count': depth_count,
                                        })

            data = response.json()['response']['items']

            if data[0]['owner_id'] == self.__owner_id:  # если паблик не найден, парсится страница обладателя токена
                print(
                    f'Для https://vk.com/{domain} не найдена страница. Возможно для нее не существует домена '
                    f'(только id).')
                continue  # скипаем итерацию

            is_last_post = True  # последний (по времени) ли пост для домена
            last_post_date = None  # время посленго поста из json-файла
            content = []  # контент, скачаенный из текущего домена

            for post in data:
                try:
                    if post['is_pinned'] == 1:  # игнорируеем закрепленные посты (таким может быть только один пост)
                        pass
                except KeyError:
                    if post['date'] <= last_post_was_lst[counter]:  # если время поста меньше (Unix)
                        break  # чем у последнего сохраненного (скаченного) поста
                        # то более рание посты смотреть нет смысла

                    if post['marked_as_ads'] != 1 and 't.me/' not in post['text'] \
                            and 'vk.com/wall' not in post['text'] and 'club' not in post[
                        'text']:  # игнорируем рекламные посты

                        tmp_content_dict = {'text': post['text']}
                        attachm_tmp = []

                        if is_last_post:
                            last_post_date = post['date']  # сохраняем дату последнего сохраненного поста
                            is_last_post = False

                        # фото
                        try:
                            for att in post['attachments']:
                                if att['type'] == 'photo':
                                    try:
                                        size_lst = []
                                        for size in att['photo']['sizes']:  # поиск фото оригинального
                                            size_lst.append(int(size['height']))  # (самого большого) размера
                                        attachm_tmp.append(att['photo']['sizes'][size_lst.index(max(size_lst))]['url'])
                                    except:
                                        attachm_tmp.append(att['photo']['sizes'][-1]['url'])  # тогда default index
                            tmp_content_dict['photo'] = attachm_tmp
                        except KeyError:
                            tmp_content_dict['photo'] = []

                        # видео и гиф (пока не работает)

                        if tmp_content_dict['text'].replace(' ', '').replace('\n', ''):
                            if tmp_content_dict['photo'] != 'Null':
                                content.append(tmp_content_dict)  # пустые посты (или возможные ошибки)
                        else:
                            if tmp_content_dict['photo']:
                                content.append(tmp_content_dict)

            if is_last_post:
                last_post_date = last_post_was_lst[counter]

            output_dict[domain] = {'last_post': last_post_date, 'content': content}  # организуем выходной словарь
            counter += 1  # увеличиваем счетчик на 1

        return output_dict

    def get_all_posts(self, domains, last_post_was_lst):
        """Парсинг последних записей. Дата последнего скаченного попоста хранится в content.json поле 'last post'.
        Если данные о последнем посте отсутствуют, то парсятся все записи в области от первой до count.
        Закрпленные и рекламные посты игнорируются."""
        data = self.__parse(domains, last_post_was_lst)
        json.dump(data, open('js/content.json', 'w', encoding="utf-8"), ensure_ascii=False)

    def get_one_test(self, domain):
        """Тест"""
        data = self.__parse([domain])
        pass
