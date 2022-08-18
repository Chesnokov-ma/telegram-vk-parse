from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import ChatNotFound, Unauthorized
from asyncio import sleep
import json


with open('js/config.json', 'r') as conf_js:  # config файл
    conf_data = json.load(conf_js)

bot = Bot(token=conf_data['tg_stat_token'])  # создание бота
dp = Dispatcher(bot, storage=MemoryStorage())  # создание диспатчера
owner_id = conf_data['tg_owner_id']


@dp.message_handler()
async def echo_messages_test(message: types.Message):       # проверка работает ли бот
    if message.from_id == owner_id:
        await bot.send_message(owner_id, 'Бот работает.')


async def get_stat(_):
    sum_all = 0
    output_message = ''
    output_dict = {}

    memb_json_is_empty = False

    with open('js/tg_channels_id.json', 'r', encoding="utf-8") as tg_json:     # данные о каналах в тг
        tg_id_data = json.load(tg_json)

    try:
        with open('js/members.json', 'r', encoding="utf-8") as memb_json:
            tg_memb_data = json.load(memb_json)
    except json.JSONDecodeError:
        memb_json_is_empty = True

    for domain in tg_id_data:
        sum_domain = 0
        for ch_name in tg_id_data[domain][1]:
            try:
                sum_domain += await bot.get_chat_members_count(ch_name)
            except ChatNotFound:
                print(f'{ch_name} не найден. Возможно в него не добавлен бот.')
                sum_domain += 0
            except Unauthorized:
                print(f'{ch_name} не является публичным.')
                sum_domain += 0

        output_message += f'{domain}: {sum_domain}'
        try:
            if not memb_json_is_empty:
                output_message += f'({sum_domain - tg_memb_data[domain]})'
        except:
            pass
        output_message += '\n'

        sum_all += sum_domain
        output_dict[domain] = sum_domain

    if not memb_json_is_empty:
        output_message += f'\nУчастников всего: {sum_all} ({sum_all - tg_memb_data["all"]})'
    else:
        output_message += f'\nУчастников всего: {sum_all}'

    output_dict['all'] = sum_all

    json.dump(output_dict, open('js/members.json', 'w', encoding="utf-8"), ensure_ascii=False)

    await bot.send_message(owner_id, output_message)       # отчет для админа
    await sleep(1)  # задержка
    quit()


def tg_stat():
    """ Сбор статистики по участникам каналов по доменам. Показ динамики с последнего сбора данных. """
    executor.start_polling(dp, skip_updates=True, on_startup=get_stat)      # запуск бота