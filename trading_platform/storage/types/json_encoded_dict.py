from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.types import TypeDecorator, VARCHAR
import simplejson as json


class JsonEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string. Taken from
    http://docs.sqlalchemy.org/en/latest/core/custom_types.html#marshal-json-strings

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# http://docs.sqlalchemy.org/en/latest/core/custom_types.html#adding-mutability
MutableJsonEncodedDict: MutableDict = MutableDict.as_mutable(JsonEncodedDict)
