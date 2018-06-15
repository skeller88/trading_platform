# TODO - DRY up this class
import traceback

from trading_platform.storage.daos.dao import Dao
from trading_platform.storage.sql_alchemy_dtos.sql_alchemy_open_order_dto import SqlAlchemyOpenOrderDto


class OpenOrderDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyOpenOrderDto)

    def fetch_by_order_id(self, session, order_id):
        try:
            dtos = session.query(self.dto_class).filter_by(order_id=order_id).all()

            if dtos is not None:
                return list(map(lambda dto: dto.to_popo(), dtos))

            return session, None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def bulk_delete_by_order_id(self, session, flush=False, commit=False, popos=None):
        order_ides = map(lambda x: x.order_id, popos) if popos is not None else []
        try:
            # synchronize the session and remove objects from the session that are deleted
            # http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.delete
            deleted_count = session.query(self.dto_class).filter(self.dto_class.order_id.in_(order_ides)).delete(
                synchronize_session='fetch')

            if flush:
                session.flush()
            if commit:
                session.commit()

            return deleted_count
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception
