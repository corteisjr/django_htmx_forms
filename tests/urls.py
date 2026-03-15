from django import forms
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView

from django_htmx_forms import HtmxFormMixin

class DummyForm(forms.Form):
    name = forms.CharField(required=True)

@method_decorator(csrf_exempt, name="dispatch")
class StandardView(HtmxFormMixin, FormView):
    template_name = "contact/page.html"
    form_class = DummyForm
    success_url = "/success/"

@method_decorator(csrf_exempt, name="dispatch")
class ExplicitTemplateView(HtmxFormMixin, FormView):
    template_name = "contact/page.html"
    htmx_template_name = "contact/custom_partial.html"
    form_class = DummyForm
    success_url = "/success/"

@method_decorator(csrf_exempt, name="dispatch")
class SuccessTemplateView(HtmxFormMixin, FormView):
    template_name = "contact/page.html"
    htmx_success_template_name = "contact/_success.html"
    form_class = DummyForm
    success_url = "/success/"

@method_decorator(csrf_exempt, name="dispatch")
class RedirectView(HtmxFormMixin, FormView):
    template_name = "contact/page.html"
    htmx_redirect = True
    form_class = DummyForm
    success_url = "/redirected/"
    
    def form_valid(self, form):
        return super().form_valid(form)

urlpatterns = [
    path("standard/", StandardView.as_view(), name="standard"),
    path("explicit/", ExplicitTemplateView.as_view(), name="explicit"),
    path("success-template/", SuccessTemplateView.as_view(), name="success-template"),
    path("redirect/", RedirectView.as_view(), name="redirect"),
]
