from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import RetryAfter, ChatNotFound
import json
import datetime
from asyncio import sleep

with open('js/config.json', 'r') as conf_js:  # config файл
    conf_data = json.load(conf_js)

bot = Bot(token=conf_data['tg_post_token'])  # создание бота
dp = Dispatcher(bot, storage=MemoryStorage())  # создание диспатчера
owner_id = conf_data['tg_owner_id']


@dp.message_handler()
async def echo_messages_test(message: types.Message):       # проверка работает ли бот
    if message.from_id == owner_id:
        await bot.send_message(owner_id, 'Бот работает.')


async def post_all(_):          # запустить бот, запостить посты, отправить информацию админу и выйключить бота
    post_sent_count = 0

    with open('js/content.json', 'r', encoding="utf-8") as content_json:   # данные о скаченных постах
        data = json.load(content_json)

    with open('js/tg_channels_id.json', 'r', encoding="utf-8") as tg_json:     # данные о каналах в тг
        tg_id_data = json.load(tg_json)

    for domain in data:
        try:
            chanels_id = tg_id_data[domain][0]     # поиск id каналов для каждого сообщества вк
            ready_to_post = True
        except KeyError:
            ready_to_post = False

        if ready_to_post:                                       # если id найдены
            for ch_id in chanels_id:                            # для каждого id
                try:
                    for post in data[domain]['content']:            # начать отправлять посты
                        try:
                            if len(post['photo']) == 1:             # если только одно фото
                                await bot.send_photo(ch_id, photo=post['photo'][0], caption=post['text'])
                                post_sent_count += 1

                            elif len(post['photo']) > 1:            # если несколько
                                media = types.MediaGroup()
                                is_first_photo = True
                                for photo_url in post['photo']:
                                    if is_first_photo:
                                        media.attach_photo(photo_url, post['text'])
                                        is_first_photo = False
                                    else:
                                        media.attach_photo(photo_url)
                                await bot.send_media_group(ch_id, media)
                                post_sent_count += 1

                            elif len(post['photo']) == 0:           # если в посте нет фото
                                # await bot.send_message(ch_id, post['text'])
                                pass                                # то лучше ничего не кидать

                        except RetryAfter:      # если пост не пропускает из-за флуда или слишком большого размера
                            pass
                        except:     # слишком много текста и все остальные исключения
                            pass

                except ChatNotFound:
                    print(f'Post-бот не добавлен в канал {ch_id}')

    # await bot.send_message(owner_id, f'Постов загружено ({datetime.datetime.now()}) : {post_sent_count}')       # отчет для админа
    print(f'({datetime.datetime.now()})\nПостов загружено: {post_sent_count}')      # тк отправка ботом ломается, вероятно из-за многопоточности
    await sleep(0.5)  # задержка
    quit()  # завершить бота


def tg_post():
    """ Запуск бота для постинга по каналам из tg_channels_id.json . Бот отправляет отчет и выключается, когда посты
    в content.json закончатся. """
    executor.start_polling(dp, skip_updates=True, on_startup=post_all)      # запуск бота
