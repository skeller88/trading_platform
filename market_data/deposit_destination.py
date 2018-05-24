class DepositDestination:
    # deposit destination status is 'ok'
    ok_status = 'ok'
    def __init__(self, address, tag, status):
        self.address = address
        self.tag = tag
        self.status = status