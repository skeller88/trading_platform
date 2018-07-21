from sqlalchemy import Integer, String, Column, Float, BigInteger

from trading_platform.strategy.strategy_execution import StrategyExecution
from trading_platform.storage.sql_alchemy_dtos.base import Base
from trading_platform.storage.types.json_encoded_dict import MutableJsonEncodedDict
from trading_platform.utils.datetime_operations import utc_timestamp


class SqlAlchemyStrategyExecutionDto(Base):
    """
    """
    __tablename__ = 'strategy_execution'

    db_id = Column(BigInteger, autoincrement=True, primary_key=True)
    strategy_execution_id = Column(String, index=True)
    strategy_id = Column(String, index=True)

    app_create_timestamp = Column(Float, nullable=False)
    version = Column(Integer, nullable=False)

    state = Column(MutableJsonEncodedDict, nullable=True)

    db_create_timestamp = Column(Float, default=utc_timestamp, nullable=False)
    db_update_timestamp = Column(Float, onupdate=utc_timestamp, nullable=True)

    def __repr__(self):
        return "<SqlAlchemyStrategyExecutionDto(db_id='%s')>" % self.db_id

    def to_popo(self):
        return StrategyExecution(
            db_id=self.db_id,
            strategy_execution_id=self.strategy_execution_id,
            strategy_id=self.strategy_id,
            app_create_timestamp=self.app_create_timestamp,
            version=self.version,
            state=self.state,
            db_create_timestamp=self.db_create_timestamp,
            db_update_timestamp=self.db_update_timestamp,
        )

    @staticmethod
    def from_popo(popo):
        return SqlAlchemyStrategyExecutionDto(
            db_id=popo.db_id,
            strategy_execution_id=popo.strategy_execution_id,
            strategy_id=popo.strategy_id,
            app_create_timestamp=popo.app_create_timestamp,
            version=popo.version,
            state=popo.state,
            db_create_timestamp=popo.db_create_timestamp,
            db_update_timestamp=popo.db_update_timestamp,
        )

