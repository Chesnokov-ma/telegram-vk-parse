import json
from vk_wall_parser import VKWallParser
from tg_post_bot import tg_post
from tg_stat_bot import tg_stat


def main():
    with open('js/config.json', 'r') as conf_js:  # config файл
        conf_data = json.load(conf_js)

    publics = open('js/domains.txt', 'r').read().replace('.', ',').replace(';', ',') \
        .replace(' ', '').replace('\n', '').split(',')  # домены сообществ
    last_post_lst = []

    with open('js/content.json', 'r', encoding="utf-8") as content_json:
        data = json.load(content_json)

    for public in publics:  # ищем информацию о последней записи в content.json
        try:
            last_post_lst.append(int(data[public]['last_post']))
        except:
            last_post_lst.append(0)  # 0 - если не находим или данные в другом формате: новый адрес для программы

    # for i in range(len(last_post_lst)):     # тест
    #     last_post_lst[i] = 0

    vkp = VKWallParser(conf_data['vk_token'], conf_data['vk_owner_id'])
    vkp.get_all_posts(publics, last_post_lst)
    print('Данные собраны')

    tg_post()
    print("Post Bot успешно завешил работу")

    tg_stat()
    print("Stat Bot успешно завешил работу")
    print('Готово')


if __name__ == '__main__':
    main()