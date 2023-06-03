from http import HTTPStatus

import stripe
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from common.views import ContextMixin
from orders.forms import OrderForm

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessTemplateView(ContextMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'Заказ оформлен'


class CanceledTemplateView(TemplateView):
    template_name = 'orders.cancel.html'


class OrderCreateView(ContextMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:order_create')
    title = 'Оформление закза'

    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1NEvlpFEClpjwQmR1eU9Anop',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_success')),
            cancel_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_canceled')),
        )
        return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super(OrderCreateView, self).form_valid(form)