# define ORM model here

# import它？

from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import FLOAT

Base=declarative_base() #生成orm基类

class Test(Base):
    # 表的名字:
    __tablename__ = 'test_chart'

    # 表的结构:
    id = Column(String(8), primary_key=True)
    mmac = Column(String(17))
    lat = Column(FLOAT(precision=10, scale=2))
    lon = Column(FLOAT(precision=10, scale=2))
    dmac = Column(String(17))
    drssi = Column(Integer())
    drange = Column(FLOAT(precision=10, scale=2))