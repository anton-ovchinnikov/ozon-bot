from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.callbacks.UserCallbackFactory import UserCallbackFactory
from bot.database.Database import Database
from bot.keyboards.menuKeyboard import get_menu_keyboard
from bot.labels.messages import START_MSG, DONT_DISTURB_DONE_ALERT
from xlsxparser.parser import parse_excel

router = Router()


async def disable_dont_disturb(database: Database, sku: int) -> None:
    await database.remove_dont_disturb(sku=sku)


@router.message(CommandStart())
async def start_cmd_handler(message: Message, database: Database) -> None:
    await message.answer(text=START_MSG)
    print(await database.read_dont_disturb())


@router.message(F.document)
async def file_handler(message: Message, database: Database, bot: Bot) -> None:
    await database.drop_goods()

    file = await bot.get_file(file_id=message.document.file_id)
    await bot.download_file(file_path=file.file_path, destination="./excel/report.xlsx")

    data = parse_excel()
    for values in data:
        await database.create_good(values=values)

    goods = await database.read_goods()
    checked_goods = []
    for good in goods:
        if {'sku': good.sku, 'cluster': good.cluster} in checked_goods:
            continue

        data = await database.read_good_by_filters(sku=good.sku, cluster=good.cluster)

        ads_data = []
        for value in data:
            try:
                idc = int(value.idc)
                if idc == 0:
                    continue
            except ValueError:
                continue

            ads = (value.count / idc)
            ads_data.append(ads)

        if len(ads_data) == 0:
            continue

        ads = max(ads_data)

        sum_count = sum([value.count for value in data])
        cluster_idc = (sum_count / ads)

        if cluster_idc >= 30:
            continue

        msg = f'Артикула {good.vendor_code} в кластере {good.cluster} осталось всего на {int(sum_count / ads)} дней!\n' \
              f'Рекомендуемое количество в поставке: {int(ads * (60 - cluster_idc))} единиц.'
        await message.answer(text=msg, reply_markup=get_menu_keyboard(sku=good.sku))
        checked_goods.append({'sku': good.sku, 'cluster': good.cluster})


@router.callback_query(UserCallbackFactory.filter())
async def dont_disturb_handler(query: CallbackQuery, scheduler: AsyncIOScheduler, database: Database,
                               callback_data: UserCallbackFactory) -> None:
    sku = callback_data.sku

    await database.add_dont_disturb(sku=sku)

    if not scheduler.get_job(f'sku', 'default'):
        scheduler.add_job(disable_dont_disturb, 'interval', start_date=datetime.now(), minutes=1, id=f'{sku}',
                          args=(database, sku,))
        scheduler.start()

        await query.answer(text=DONT_DISTURB_DONE_ALERT)
