from trading_platform.storage.daos.dao import Dao
from trading_platform.storage.sql_alchemy_dtos.sql_alchemy_balance_dto import SqlAlchemyBalanceDto


class BalanceDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyBalanceDto)
