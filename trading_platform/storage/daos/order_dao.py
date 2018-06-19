# TODO - DRY up this class
import traceback
from typing import Optional, List

from trading_platform.exchanges.data.order import Order
from trading_platform.storage.daos.dao import Dao
from trading_platform.storage.sql_alchemy_dtos.sql_alchemy_order_dto import SqlAlchemyOrderDto


class OrderDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyOrderDto)

    def fetch_earliest_with_order_id(self, session, order_id) -> Optional[Order]:
        """
        Fetch the order with the earliest app_create_timestamp.
        Args:
            session:
            order_id:

        Returns:

        """
        try:
            dto = session.query(self.dto_class).filter_by(order_id=order_id).order_by(
                SqlAlchemyOrderDto.app_create_timestamp).first()

            if dto is not None:
                return dto.to_popo()

            return None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def fetch_latest_with_order_id(self, session, order_id) -> Optional[Order]:
        """
        Fetch the order with the most recent/latest order_status and app_create_timestamp. This logic depends on
        the possible order statuses in OrderStatus being ints in chronological order. In other words,
        OrderStatus.pending == 0, and OrderStatus.open == 1. An order will always be pending before it is open.
        Args:
            session:
            order_id:

        Returns:

        """
        try:
            dto = session.query(self.dto_class).filter_by(order_id=order_id).order_by(
                SqlAlchemyOrderDto.order_status.desc(), SqlAlchemyOrderDto.app_create_timestamp.desc()).first()

            if dto is not None:
                return dto.to_popo()

            return None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def fetch_by_order_id(self, session, order_id) -> List:
        try:
            dtos = session.query(self.dto_class).filter_by(order_id=order_id).all()

            if dtos is not None:
                return list(map(lambda dto: dto.to_popo(), dtos))

            return []
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception
