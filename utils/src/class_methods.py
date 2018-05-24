def custom_eq(self, other):
    """
    Based off this SO answer:
    https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes

    Overrides the default implementation of __eq__
    """
    if isinstance(self, other.__class__):
        for k, v in self.__dict__.items():
            if self.__dict__.get(k) != other.__dict__.get(k):
                print('Instance attribute {0}: expected {1}, got {2}'.format(k, v, other.__dict__.get(k)))
                return False
        return True
    return False


def custom_hash(self):
    """Overrides the default implementation of __hash__"""
    return hash(tuple(sorted(self.__dict__.items())))