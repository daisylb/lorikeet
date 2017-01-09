Lorikeet
========

⚠️ **Note:** Lorikeet is a work in progress. It may change at any time,
and you shouldn't use it in production yet.

Lorikeet is a simple, generic, API-only shopping cart framework for
Django.

Design Goals
------------

-  **Be customisable, without being overbearing.** Rather than providing
   an extremely complex application with bells, whistles and
   configuration options to satisfy every use case, lorikeet provides a
   shopping cart framework, on top of which you can build your online
   store. In this regard, Lorikeet is heavily inspired by
   `Django-SHOP <https://django-shop.readthedocs.io/en/latest/architecture.html>`__.
-  **Be minimal.** Lorikeet's sole concern is the shopping cart and
   checkout process. Lorikeet has no knowledge of things like products,
   variations, categories, and so on, nor does it contain views to
   display these things. This is in keeping with the previous design
   goal, because it allows you to structure both the data model and UI
   of your products in a way that makes sense for the site you're
   building.
-  **Be loosely coupled.** While Lorikeet was originally built as part
   of an online store that uses Django CMS and React, it does not depend
   on either, and could be used with any CMS or frontend framework, or
   none at all. Lorikeet provides an optional companion set of reusable
   React components for the checkout experience, but the REST API used
   to manipulate the cart is well-documented and considered part of the
   library's public API surface.
-  **Get out of the way.** One of the core design goals of the project
   Lorikeet was extracted from is to provide a simple, low-friction
   checkout experience. Lorikeet was designed from the ground up to
   enable this.
