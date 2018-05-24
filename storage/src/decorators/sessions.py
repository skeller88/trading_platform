"""
Great tutorial on decorators: https://www.python-course.eu/python3_decorators.php

Decorators related to session management
"""


# Modeled after http://docs.sqlalchemy.org/en/latest/faq/sessions.html
# The 'func' is passed to 'session_decorator', and session parameters
# are passed into 'with_session', and the parameters of 'func' are passed to 'execute'.
def with_write_session(session, flush, commit):
    def session_decorator(func):
        def execute(*args, **kw):
            session.begin(subtransactions=True)
            try:
                result = func(*args, **kw)
                if flush:
                    session.flush()
                if commit:
                    print('committing')
                    session.commit()
                return session, result
            except Exception as exception:
                print('rolling back due to exception')
                session.rollback()
                raise exception
        return execute
    return session_decorator


def with_read_session(session):
    def session_decorator(func):
        def execute(*args, **kw):
            session.begin(subtransactions=True)
            try:
                result = func(*args, **kw)
                return session, result
            except Exception as exception:
                print('rolling back due to exception')
                session.rollback()
                raise exception
        return execute
    return session_decorator
