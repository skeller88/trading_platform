from arbitrage_executer.src.market_data.arbitrage_attempt import ArbitrageAttempt
from trading_platform.exchanges.data.order import Order
from core.src.storage import s3_operations


def main(write_to_s3, arbitrage_attempt_dao, order_dao, session, start_processing_time):
    """
    Get a snapshot of arbitrage attempts and orders. Ideally the database would be directly queried via a local
    script, but due to RDS security rules, that is not possible. We could also query via an EC2 instance, but that's
    annoying to have to spin up and shut down the EC2 instance.

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
        write_to_s3:
        arbitrage_attempt_dao:
        order_dao:
        session:
        start_processing_time:

    Returns:

    """
    arbitrage_attempts = arbitrage_attempt_dao.filter_processing_time_greater_than(session=session,
                                                                                   processing_time=start_processing_time)
    orders = order_dao.filter_processing_time_greater_than(session=session, processing_time=start_processing_time)

    aa_filepath = s3_operations.write_result(write_to_s3=write_to_s3, bucket='arbitrage-bot',
                                             results=arbitrage_attempts,
                                             result_class=ArbitrageAttempt,
                                             file_version=ArbitrageAttempt.current_version,
                                             filename_date_suffix=False) if len(
        arbitrage_attempts) > 0 else None

    order_filepath = s3_operations.write_result(write_to_s3=write_to_s3, bucket='arbitrage-bot', results=orders,
                                                result_class=Order, file_version=Order.current_version,
                                                filename_date_suffix=False) if len(
        orders) > 0 else None
    return {
        'arbitrage_attempts_filepath': aa_filepath,
        'order_filepath': order_filepath
    }
