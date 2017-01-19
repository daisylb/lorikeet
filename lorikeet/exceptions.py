class PaymentError(Exception):
    """Represents an error accepting payment on a PaymentMethod.

    :param info: A JSON-serializable object containing details of the problem,
        to be passed to the client.
    """

    def __init__(self, info=None):
        self.info = info


class IncompleteCartError(Exception):
    """Represents a reason that a cart is not ready for checkout.

    Similar to a Django ``ValidationError``, but not used to reject a change
    based on submitted data.

    :param code: A consistent, non-localised string to identify the specific
        error.
    :type code: str
    :param message: A human-readable message that explains the error.
    :type message: str
    :param field: The field that the error relates to. This should match one
        of the fields in the cart's serialized representation, or be set to
        ``None`` if a specific field does not apply.
    :type field: str, NoneType
    """

    def __init__(self, code, message, field=None):
        self.code = code
        self.message = message
        self.field = field

    def to_json(self):
        """Returns the error in a JSON-serializable form.

        :rtype: dict
        """
        return {
            'code': self.code,
            'message': self.message,
            'field': self.field,
        }

    def __key(self):
        return (self.code, self.message, self.field)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


class IncompleteCartErrorSet(IncompleteCartError):
    """Represents a set of multiple reasons a cart is not ready for checkout.

    You can raise this exception instead of
    :class:`~lorikeet.exceptions.IncompleteCartError`
    if you would like to provide multiple errors at once.

    This class is iterable.

    :param errors: All of the errors that apply.
    :type errors: Iterable[IncompleteCartError]
    """

    def __init__(self, errors=()):
        self.errors = list(errors)

    def to_json(self):
        """Returns the list of errors in a JSON-serializable form.

        :rtype: dict
        """
        return [x.to_json() for x in self.errors]

    def add(self, error):
        """Add a new error to the set.

        :param error: The error to add. If an
            :class:`~lorikeet.exceptions.IncompleteCartErrorSet` instance
            is passed, it will be merged into this one.
        :type error: IncompleteCartError, IncompleteCartErrorSet
        """

        if isinstance(error, IncompleteCartErrorSet):
            self.errors += error.errors
        else:
            self.errors.append(error)

    def __bool__(self):
        return bool(self.errors)

    def __iter__(self):
        return iter(self.errors)
