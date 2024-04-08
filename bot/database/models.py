from sqlalchemy import Column, Integer, BigInteger, Text

from bot.database.base import Base


class Good(Base):
    __tablename__ = 'goods'

    id = Column(Integer, primary_key=True)
    sku = Column(BigInteger, nullable=False)
    store = Column(Text, nullable=True)
    vendor_code = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    count_in_transit = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    reserve = Column(Integer, nullable=False)
    idc = Column(Text, nullable=False)
    cluster = Column(Text, nullable=False)


class DontDisturb(Base):
    __tablename__ = 'dont_disturb'

    id = Column(Integer, primary_key=True)
    sku = Column(BigInteger, nullable=False)
