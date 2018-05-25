# TODO - DRY up this class
import traceback

from trading_platform.storage.src.daos.dao import Dao
from trading_platform.storage.src.sql_alchemy_dtos.sql_alchemy_order_dto import SqlAlchemyOrderDto


class OrderDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyOrderDto)

    def fetch_earliest_with_order_index(self, session, order_index):
        """
        Fetch the order with the earliest processing_time.
        Args:
            session:
            order_index:

        Returns:

        """
        try:
            dto = session.query(self.dto_class).filter_by(order_index=order_index).order_by(
                SqlAlchemyOrderDto.processing_time).first()

            if dto is not None:
                return dto.to_popo()

            return None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def fetch_latest_with_order_index(self, session, order_index):
        """
        Fetch the order with the most recent/latest processing_time. Only used in testing for now to check
        updated Order state after an arbitrage step.
        Args:
            session:
            order_index:

        Returns:

        """
        try:
            dto = session.query(self.dto_class).filter_by(order_index=order_index).order_by(
                SqlAlchemyOrderDto.processing_time.desc()).first()

            if dto is not None:
                return dto.to_popo()

            return None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def fetch_by_order_index(self, session, order_index):
        try:
            dtos = session.query(self.dto_class).filter_by(order_index=order_index).all()

            if dtos is not None:
                return list(map(lambda dto: dto.to_popo(), dtos))

            return session, None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception
