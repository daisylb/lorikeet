class PaymentError(Exception):
    """Represents an error accepting payment on a PaymentMethod.

    :param info: A JSON-serializable object containing details of the problem,
        to be passed to the client.
    """

    def __init__(self, info=None):
        self.info = info
