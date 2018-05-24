"""
Load the classes for the necessary tables so that SqlAlchemy MetaData can create associations between Dto classes
and Postgres tables.
"""
from storage.src.sql_alchemy_dtos.sql_alchemy_balance_dto import SqlAlchemyBalanceDto
from storage.src.sql_alchemy_dtos.sql_alchemy_order_dto import SqlAlchemyOrderDto
from storage.src.sql_alchemy_dtos.sql_alchemy_ticker_dto import SqlAlchemyTickerDto


def exchange_data_tables():
    return [
        SqlAlchemyBalanceDto,
        SqlAlchemyOrderDto,
        SqlAlchemyTickerDto
    ]
