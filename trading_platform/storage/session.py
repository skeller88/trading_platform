from sqlalchemy import orm


class Session(orm.Session):
    """
    Bridge class.
    """