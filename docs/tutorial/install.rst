Installation
============

This tutorial assumes you have an existing Django project set up. If you don't, you can create one with `startproject <https://docs.djangoproject.com/en/2.2/ref/django-admin/#startproject>`_.

1. Install Lorikeet, by running ``pip install lorikeet``.
2. Add ``'lorikeet'`` to ``INSTALLED_APPS``.
3. Add ``'lorikeet.middleware.CartMiddleware'`` to ``MIDDLEWARE_CLASSES``.
4. Add a line that looks like ``url(r'^_cart/', include('lorikeet.urls', namespace='lorikeet')),`` to ``urls.py``. (You don't have to use ``_cart`` in your URL—anything will do.)

You're all set! If you run ``python manage.py runserver`` and visit ``http://localhost:8000/_cart/``, you should see a JSON blob with a few properties. Now you're ready to start building your backend!
