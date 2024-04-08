from sqlalchemy import select, ScalarResult, delete
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Good, DontDisturb


# noinspection PyTypeChecker
class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_good(self, values: dict) -> None:
        stmt = insert(Good).values(**values).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

    async def drop_goods(self) -> None:
        stmt = delete(Good)
        await self.session.execute(stmt)
        await self.session.commit()

    async def read_goods(self) -> ScalarResult:
        dont_disturb = await self.read_dont_disturb()
        stmt = select(Good).filter(Good.sku.not_in(dont_disturb))
        good = await self.session.execute(stmt)
        return good.scalars().all()

    async def read_good_by_filters(self, **filters) -> ScalarResult:
        dont_disturb = await self.read_dont_disturb()
        stmt = select(Good).filter(Good.sku.not_in(dont_disturb)).filter_by(**filters)
        good = await self.session.execute(stmt)
        return good.scalars().all()

    async def add_dont_disturb(self, sku: int) -> None:
        stmt = insert(DontDisturb).values(sku=sku).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

    async def read_dont_disturb(self) -> list[int]:
        stmt = select(DontDisturb.sku)
        dont_disturb = await self.session.execute(stmt)
        return dont_disturb.scalars().all()

    async def remove_dont_disturb(self, sku: int) -> None:
        stmt = delete(DontDisturb).where(DontDisturb.sku == sku)
        await self.session.execute(stmt)
        await self.session.commit()
