from trading_platform.storage.daos.dao import Dao
from trading_platform.storage.sql_alchemy_dtos.strategy_execution_dto import SqlAlchemyStrategyExecutionDto


class StrategyExecutionDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyStrategyExecutionDto)
