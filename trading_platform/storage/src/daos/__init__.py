"""
These classes are wrapper classes of whatever ORM or SQL framework is used. Capabilities of each class:
- translating the Python object to and from a DAO object
- CRUD operations
- creating sessions or using an existing session
- committing or flushing a session to the database

Why convert to a POPO? Because then the database
logic bound to the DAO is decoupled from the application logic. If in the future the database logic needs to be
changed dramatically, the application logic shouldn't be aware of that. This is especially important when creating or
updating an entity to ensure that the dao reflects the post-commit/post-flush state of the entity in the database.
For example, until a new entity is committed to the database, its dao.db_id is None. Don't convert from a dao to a POPO until after database
operations are complete.
"""