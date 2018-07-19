from trading_platform.storage.daos.dao import Dao
from trading_platform.storage.sql_alchemy_dtos.strategy_dto import SqlAlchemyStrategyDto


class StrategyDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyStrategyDto)
