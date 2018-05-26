"""
Miscellaneous mocks using MagicMock. If there get to be enough mocks in here, I'll refactor.
"""


class DaoMock:
    @staticmethod
    def bulk_save(session, flush=False, commit=False, popos=None):
        return session, popos