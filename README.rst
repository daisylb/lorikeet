Lorikeet
========

⚠️ **Note:** Lorikeet is a work in progress. It may change at any time,
and you shouldn't use it in production yet.

Lorikeet is a simple, generic, API-only shopping cart framework for
Django.

Lorikeet currently supports Django 1.8 to 1.10 on Python 3.4+. New versions of Lorikeet will support `Django versions that currently have extended support <https://www.djangoproject.com/download/#supported-versions>`_.

Design Goals
------------

- **Simple.** Lorikeet isn't an *e-commerce framework*, it's a *shopping cart framework*. It provides a cart that end users can put things in, attach a delivery address to, pick a payment method, and check out; everything else, including the product pages themselves, is left up to you to do in a way that best suits your needs. (This also means Lorikeet can be used with Wagtail, Mezzanine, Django CMS, another CMS, or none at all!)
- **Generic.** Lorikeet is a framework, not an app. Instead of trying to be all things to all people, Lorikeet lets you define your own models for line items, delivery addresses and payment methods. This means that simple sites only take a few lines of code, and are free of unneeded complexity; complex sites can be tailored to their specific needs rather than trying to shoe-horn a solution.
- **API-only.** One of Lorikeet's main goals is to enable you to create a fast, frictionless checkout experience. The easiest way to do this is with an API.
