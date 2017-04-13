Recipes
=======

Stock Levels
------------

.. todo::

    Describe how to use ``check_complete`` and ``prepare_for_checkout`` to track stock-levels without race conditions.

.. todo::

    Figure out how a higher-traffic site that doesn't want to effectively serialise purchases of a particular product might implement it differently.

External Invoice IDs
--------------------

Ideally, you'd be able to use the auto-incrementing primary key of the :class:`~lorikeet.models.Order` table as your invoice ID. But what if you're using special snowflake accounting software that won't let you insert an invoice with an ID you've supplied, instead insisting on generating one itself?

Lorikeet provides a ``LORIKEET_INVOICE_ID_GENERATOR`` setting which lets you provide custom invoice numbers, but you probably don't want to communicate with your accounting software from there; it's called as part of the checkout process, and calling a remote API from there is a good way to introduce a point of failure at a critical part of the purchasing process.

Instead, create a single-column model, generate some draft invoices in your accounting software, and insert their IDs into it:

::

    class InvoiceID(models.Model):
        number = models.CharField(max_length=11, primary_key=True)

Then, in your ``LORIKEET_INVOICE_ID_GENERATOR`` function, pick the next available invoice ID and return it.

::

    def get_invoice_id():
        row = InvoiceID.objects.select_for_update(skip_locked=True).first()
        number = row.number
        row.delete()
        return number

.. note::

    The ``.select_for_update(skip_locked=True)`` part of this snippet is important; without it, you'll end up serialising checkouts, so if two people check out one of them will block until the other is finished. Unfortunately, it's only supported in Django 1.11+ on PostgreSQL and Oracle.

    If you're running an older version of Django, but are still using PostgreSQL, you can execute the equivalent raw SQL instead::

        from django.db import connection

        def get_invoice_number():
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM products_invoiceid
                    WHERE number = (
                        SELECT number
                        FROM products_invoiceid
                        ORDER BY number
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    RETURNING number;
                """)
                return cursor.fetchone()[0]