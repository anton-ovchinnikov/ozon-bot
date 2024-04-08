import asyncio
import logging

from aiogram import Dispatcher, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncConnection

from bot.database.Database import Database
from bot.database.base import Base
from bot.handlers import menuHandlers
from bot.middlewares.DatabaseMiddleware import DatabaseMiddleware
from bot.middlewares.SchedulerMiddleware import SchedulerMiddleware
from configreader import config


async def main() -> None:
    logging.basicConfig(format='[%(asctime)s - %(name)s] %(levelname)s: %(message)s', level=logging.INFO)

    dp = Dispatcher()
    bot = Bot(token=config.BOT_TOKEN, parse_mode='html', protect_content=True)

    engine = create_async_engine(f"sqlite+aiosqlite:///database.sqlite", future=True, echo=True)

    conn: AsyncConnection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = async_sessionmaker(engine, expire_on_commit=True).begin().async_session
    await session.commit()
    database = Database(session=session)

    scheduler = AsyncIOScheduler()

    dp.include_router(router=menuHandlers.router)

    dp.message.middleware(DatabaseMiddleware(database=database))
    dp.callback_query.middleware(DatabaseMiddleware(database=database))
    dp.callback_query.middleware(SchedulerMiddleware(scheduler=scheduler))
    dp.callback_query.middleware(SchedulerMiddleware(scheduler=scheduler))

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        await session.close()
        await engine.dispose()
        await bot.close()


asyncio.run(main())
