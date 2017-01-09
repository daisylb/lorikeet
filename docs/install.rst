Installation
============

This tutorial assumes you have an existing Django project set up. If you don't, you can create one with `startproject <https://docs.djangoproject.com/en/1.10/ref/django-admin/#startproject>`_.

1. Install Lorikeet, by running ``pip install https://gitlab.com/abre/lorikeet.git``.
2. Add ``'lorikeet'`` to ``INSTALLED_APPS``.
3. Add ``'lorikeet.middleware.CartMiddleware'`` to ``MIDDLEWARE_CLASSES``.
4. Add a line that looks like ``url(r'^_cart/', include('lorikeet.urls', namespace='lorikeet')),`` to ``urls.py``. (You don't have to use ``_cart`` in your URL—anything will do.)
5. You're all set, and ready to start building your backend!
