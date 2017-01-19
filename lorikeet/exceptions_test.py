from . import exceptions


def test_cart_error_set_combination():
    es = exceptions.IncompleteCartErrorSet()
    a = exceptions.IncompleteCartError('a', 'a')
    b = exceptions.IncompleteCartError('b', 'b')
    es.add(a)
    es.add(b)

    assert es.errors == [a, b]


def test_cart_error_set_flattens():
    es = exceptions.IncompleteCartErrorSet()
    a = exceptions.IncompleteCartError('a', 'a')
    b = exceptions.IncompleteCartError('b', 'b')
    c = exceptions.IncompleteCartError('c', 'c')
    es.add(a)
    es.add(exceptions.IncompleteCartErrorSet((b, c)))

    assert es.errors == [a, b, c]
