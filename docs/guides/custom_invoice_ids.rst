Custom Invoice IDs
==================

Lorikeet provides a setting, :data:`LORIKEET_INVOICE_ID_GENERATOR`, which can be set to the import path of a function that returns a string to use as an invoice ID. For example, given the function below in ``myapp/invoice_id.py``, you'd set the setting to ``myapp.invoice_id.invoice_uuid``.

::

    from uuid import uuid4

    def invoice_uuid():
        return uuid4()

The function is run inside a transaction, but it doesn't get a child transaction of its own, so if you plan on catching database errors inside the transaction you'll need to wrap your code in a sub-transaction.

The ID generator is run when an Order is created, which is just before the user's payment method is charged. This means that if payment fails, the invoice that's generated may not be used; however the database transaction will be rolled back.

Lorikeet enforces the uniqueness of custom invoice IDs at the database level, and trying to reuse one will result in a 500 response at checkout; your invoice ID generator is responsible for ensuring it never returns the same value twice.

When Not To Use This Feature
----------------------------

If you can, use the auto-incrementing primary key of the :class:`~lorikeet.models.Order` table as your invoice ID.

Sometimes it's desirable to give the first invoice issued a number other than one, so that your first customer doesn't realise they're your first customer, or so that your invoice numbers don't overlap with invoices issued by a previous system. The best way to accomplish this is to update the database sequence, for example on Postgres:

.. code-block:: sql

    ALTER SEQUENCE lorikeet_order_id_seq
    MINVALUE 38146
    START WITH 38146
    RESTART;

Getting Invoice IDs From Remote Systems
---------------------------------------

If you're using accounting software that won't let you insert an invoice with an ID you've supplied, instead insisting on generating one itself, you will need to use this feature.

However, you probably don't want to communicate with your accounting software from within your ID generator; it's called as part of the checkout process, and calling a remote API over a network from there is a good way to introduce a point of failure at a critical part of the purchasing process.

Instead, create a single-column model, generate some draft invoices in your accounting software, and insert their IDs into it:

::

    class InvoiceID(models.Model):
        number = models.CharField(max_length=11, primary_key=True)

Then, in your invoice ID generator function, pick the next available invoice ID and return it.

::

    def get_invoice_id():
        row = InvoiceID.objects.select_for_update(skip_locked=True).first()
        number = row.number
        row.delete()
        return number

.. note::

    The ``skip_locked=True`` part of this snippet is important; without it, you'll end up serialising checkouts, so if two people check out one of them will block until the other is finished. (Remember, the entire checkout process happens within a transaction, which could run as slow as multiple seconds depending on how fast your payment provider is.) Unfortunately, it's only supported in Django 1.11+ on PostgreSQL and Oracle.

    You also can't remove ``select_for_update()`` altogether; if you do, you'll end up trying to assign multiple purchases the same invoice ID, resulting in crashes.

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
