import math
import os

import sys
add = os.getcwd()
sys.path.append(add)
from database_snapshot.src import snapshot
from core.src.properties.env_properties import EnvProperties
from arbitrage_executer.src.daos.arbitrage_attempt_dao import ArbitrageAttemptDao
from trading_platform.storage.daos.order_dao import OrderDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine


def main(event, context):
    """
    Fetching by processing time should be an efficient operation since that field is indexed. It can
    be safely assumed that all of the orders for an arbitrage attempt will be returned because the processing_time
    for both arbitrage_attempt (aa) and order is set during instantiation, and aa is instantiated after
    orders are instantiated.

    It's possible, though unlikely, that the start_processing_time could be > the processing_time of one order for an
    aa, and < processing_time of the other order. There doesn't seem to be an easy way to detect that, because the number
    of orders for a given arbitrage could be any number. For example, there could be two orders if the orders are filled
    right away. But there could be 5 orders if one order was filled after 2 executions of the app, and the other
    was filled after 3 executions. TODO - figure out how to detect this edge case.

    Args:
        arbitrage_attempt_dao:
        order_dao:
        session:
        start_processing_time:

    Returns:

    """
    engine = SqlAlchemyEngine.rds_engine() if EnvProperties.is_prod else SqlAlchemyEngine.local_engine_maker()
    session = engine.scoped_session_maker()
    arbitrage_attempt_dao = ArbitrageAttemptDao()
    order_dao = OrderDao()

    return snapshot.main(arbitrage_attempt_dao=arbitrage_attempt_dao, order_dao=order_dao, session=session,
                         write_to_s3=EnvProperties.is_prod, start_processing_time=-math.inf)
