import traceback


class Dao:
    def __init__(self, dto_class):
        self.dto_class = dto_class

    # Create
    def save(self, session, flush=False, commit=False, popo=None):
        try:
            dto = self.dto_class.from_popo(popo)
            session.add(dto)

            if flush:
                session.flush()
            if commit:
                session.commit()

            return session, dto.to_popo()
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def bulk_save(self, session, flush=False, commit=False, popos=None):
        try:
            dtos = [self.dto_class.from_popo(popo) for popo in popos]
            session.add_all(dtos)

            if flush:
                session.flush()
            if commit:
                session.commit()

            saved = [dto.to_popo() for dto in dtos]
            return session, saved
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    # Read
    def fetch_by_db_id(self, session, db_id):
        try:
            dto = session.query(self.dto_class).filter_by(db_id=db_id).first()

            if dto is not None:
                return session, dto.to_popo()

            return session, None
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def fetch_all(self, session):
        try:
            dtos = session.query(self.dto_class).all()

            if dtos is not None:
                return session, list(map(lambda dto: dto.to_popo(), dtos))

            return session, []
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def filter_processing_time_greater_than(self, session, processing_time):
        try:
            dtos = session.query(self.dto_class).filter(self.dto_class.processing_time >= processing_time).order_by(self.dto_class.processing_time).all()

            if dtos is not None:
                return list(map(lambda dto: dto.to_popo(), dtos))

            return []
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    # Update
    def update(self, session, db_id, update_dict={}, commit=False, flush=False):
        """

        Args:
            session:
            flush:
            commit:
            db_id:
            update_dict:

        Returns:

        """
        try:
            session.query(self.dto_class).filter(self.dto_class.db_id == db_id).update(update_dict)

            if flush:
                session.flush()
            if commit:
                session.commit()

        except Exception as exception:
            print('rolling back due to exception')
            session.rollback()
            raise exception

    # Delete
    def delete(self, session, db_id, flush=False, commit=False):
        try:
            deleted_count = session.query(self.dto_class).filter_by(db_id=db_id).delete()

            if flush:
                session.flush()
            if commit:
                session.commit()

            return session, deleted_count
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception

    def delete_all(self, session, flush=False, commit=False):
        try:
            deleted_count = session.query(self.dto_class).delete()

            if flush:
                session.flush()
            if commit:
                session.commit()

            return session, deleted_count
        except Exception as exception:
            print('rolling back due to exception')
            traceback.print_exc()
            session.rollback()
            raise exception