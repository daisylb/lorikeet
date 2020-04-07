Lorikeet
========

⚠️ **Note:** Lorikeet is a work in progress. It may change at any time,
and you shouldn't use it in production yet.

Lorikeet is a simple, generic, API-only shopping cart framework for
Django.

Lorikeet currently supports Django 2.2 and 3.0 on Python 3.6+. New versions of Lorikeet will support `Django versions that currently have extended support <https://www.djangoproject.com/download/#supported-versions>`_.

Why use Lorikeet?
-----------------

E-commerce apps are divided into two types: simple ones that work well so long as what you're selling is simple, and complex ones that try to be all things to all people by way of a maze of checkboxes and dropdowns.

**Lorikeet isn't an e-commerce app; it's a shopping cart framework.** With Lorikeet, you define models for line items (the things that go in your cart), delivery addresses and payment methods yourself. For complex shops, this means you can model exactly the functionality you need without fighting the system. For simple shops, this is a simple process that requires way less code than you'd expect, and gives you a system without unnecessary bloat, but with room to grow.

**Lorikeet only cares about the cart itself**; everything outside of that, including your navigation and product pages, is directly under your control, so you're free to use a simple ``ListView`` and ``DetailView``, Wagtail, Mezzanine, Django CMS, or something totally bespoke. There's not a single line of HTML or CSS in Lorikeet's codebase either, so Lorikeet gives you total control over your visuals too.

Lorikeet line items, delivery addresses and payment methods are designed to be orthogonal, so you can package them as reusable apps and share them internally between sites in your company, or with the world as open-source packages. In fact, **Lorikeet already includes an optional Stripe payment method plugin**, totally separate from the rest of the codebase and written against the same public API as your own apps.

Because most modern payment providers require JavaScript anyway, **Lorikeet is API-only**. This lets you build a fast, frictionless shopping experience where users can add to and change their shopping carts without the entire page refreshing each time, and Lorikeet's API is designed to allow logged-in repeat users to check out in a single click.


Why use something else?
-----------------------

- **Lorikeet isn't turnkey.** For simple sites, you won't need to write much Python code; for complex ones, the time it takes to get up and running will probably be comparable to the time it takes to figure out how to bend e-commerce apps to your will. But the total control over the frontend that Lorikeet gives you means you'll need to write a fair bit of HTML, CSS and JavaScript to get up and running, so if you need to go from zero to shop quickly, it's best to look somewhere else.
- **Lorikeet sites will require JavaScript.** Lorikeet doesn't provide regular HTML-form-based views for adding items to the cart and checking out; if you need this, Lorikeet isn't for you.
