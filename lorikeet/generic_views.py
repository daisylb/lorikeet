import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.signing import BadSignature
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, ListView

from . import models
from .settings import order_url_signer

logger = logging.getLogger(__name__)

ORDER_SESSION_KEY_TEMPLATE = 'lorikeet-order-{}-access'


class OrderDetailView(DetailView):
    """A view that displays a single order."""

    model = models.Order

    def get(self, request, *args, **kwargs):
        # Remove the order access token from the URL before we ever display
        # a page, to avoid leaking it to third-party services; see also
        # https://robots.thoughtbot.com/is-your-site-leaking-password-reset-links
        # This token is not quite as high-value as a password reset token,
        # but we should probably do the right thing anyway.
        if 'token' in request.GET:
            new_query = request.GET.copy()
            token = new_query.pop('token')
            try:
                order_id = order_url_signer.unsign(token[0])
            except BadSignature:
                # A 404 page with the token in the URL could still be dangerous
                # (in case the token is mostly correct but not entirely), so
                # redirect to the non-tokenized URL w/o setting the session
                # so that it 404s there instead.
                logger.debug("Bad signature: %r", token[0])
            else:
                session_key = ORDER_SESSION_KEY_TEMPLATE.format(order_id)
                request.session[session_key] = True

            if new_query:
                return HttpResponseRedirect('{}?{}'.format(
                    request.path, new_query.urlencode()
                ))
            else:
                return HttpResponseRedirect(request.path)

        return super().get(request, *args, **kwargs)

    def get_object(self):
        the_id = self.kwargs['id']
        session_key = ORDER_SESSION_KEY_TEMPLATE.format(the_id)
        if session_key in self.request.session:
            return models.Order.objects.get(id=the_id)
        elif self.request.user.is_authenticated():
            return models.Order.objects.get(
                user=self.request.user,
                id=the_id,
            )
        else:
            raise Http404()


class OrderListView(LoginRequiredMixin, ListView):
    """A view that displays a list of orders belonging to a user."""

    def get_queryset(self):
        return models.Order.objects.filter(
            user=self.request.user).order_by('-id')
