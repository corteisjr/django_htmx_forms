[![PyPI version](https://img.shields.io/pypi/v/django-htmx-form-mixin)](https://pypi.org/project/django-htmx-form-mixin/)
[![Tests](https://github.com/corteisjr/django_htmx_forms/actions/workflows/test.yml/badge.svg)](https://github.com/corteisjr/django_htmx_forms/actions)
[![Python versions](https://img.shields.io/pypi/pyversions/django-htmx-form-mixin)](https://pypi.org/project/django-htmx-form-mixin/)

# django-htmx-forms

A clean, zero-boilerplate mixin to seamlessly integrate Django Forms with HTMX. 

The core idea is simple: when form validation fails, instead of reloading the entire page, the server returns **only the updated form fragment** (containing the inline validation errors).

## Why does this exist?

By default, Django's `FormView` triggers a full page reload when a form is invalid. When building modern interfaces with HTMX, you usually want to swap only the form HTML to display inline validation errors. Doing this manually requires you to:

- Detect if the request came from HTMX
- Choose a partial template fragment instead of the full page template
- Return the correct HTTP status code for HTMX to understand

**`django-htmx-forms` encapsulates this entire behavior into a single, highly intuitive mixin.**

## Installation

Currently, you can install the package directly from the repository, or simply copy the `HtmxFormMixin` into your project.

You do **not** need to add it to your `INSTALLED_APPS` since it's just a class-based view mixin.

## Requirements

- Python 3.8+
- Django 3.2+
- HTMX on the frontend
- *(Optional)* `django-htmx` - The mixin natively supports it and will check `request.htmx` if available.

## Quick Start

### 1. View configuration

Simply inherit from `HtmxFormMixin` **before** the standard Django `FormView` (or `CreateView` / `UpdateView`):

```python
# views.py
from django.views.generic import FormView
from django_htmx_forms import HtmxFormMixin
from .forms import ContactForm

class ContactView(HtmxFormMixin, FormView):
    template_name = "contact/page.html"
    form_class = ContactForm
    success_url = "/thanks/"
```

### 2. Full Page Template (`contact/page.html`)

Include the HTMX `response-targets` extension (see the **Handling 422 Responses** section below) and configure your form wrapper to handle the POST request.

```html
<!-- Include HTMX and the response-targets extension -->
<script src="https://unpkg.com/htmx.org@1.9.12"></script>
<script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/response-targets.js"></script>

<!-- Setup the wrapper -->
<div id="form-wrapper" hx-ext="response-targets">
    {% include "contact/_form.html" %}
</div>
```

### 3. Form Partial Template (`contact/_form.html`)

Put your form logic inside a partial template. This is the fragment that will be swapped upon validation errors.

```html
<form method="post"
      hx-post="{% url 'contact' %}"
      hx-target="#form-wrapper"
      hx-target-4xx="#form-wrapper"
      hx-swap="innerHTML">
    
    {% csrf_token %}
    {{ form.as_p }}
    
    <button type="submit">Send</button>
</form>
```

## How It Works

- **HTMX Requests:**
  - `form_invalid()`: Renders only the form partial and returns an **HTTP 422 (Unprocessable Entity)** status code.
  - `form_valid()`: You can configure it to either swap a success fragment (`htmx_success_template_name`) or send an `HX-Redirect` header (`htmx_redirect = True`).
- **Standard Requests:** Modifies nothing. The default Django behavior is preserved for non-HTMX requests (graceful degradation).

### Automatic Template Resolution

If you do **not** explicitly define an `htmx_template_name`, the mixin is smart enough to derive the partial template name based on your `template_name`.

For example, if your `template_name` is `"contact/page.html"`, the mixin will look for templates in exactly this order:
1. `"contact/_form.html"` *(The standard convention)*
2. `"contact/_page.html"`
3. `"contact/page.html"` *(Fallback to the full page if no partial is found)*

This enables a true **zero-configuration** experience if you follow the `_form.html` naming convention.

---

## ⚠️ Important: Handling 422 Responses in HTMX

By design, this mixin returns an **HTTP 422 Unprocessable Entity** status when form validation fails. This is the semantically correct HTTP status code for validation errors.

However, **HTMX ignores non-200 responses by default** and will not swap the content. To ensure the validation errors are displayed correctly, you **must** use the HTMX [response-targets extension](https://htmx.org/extensions/response-targets/).

1. Include the extension script in your HTML `<head>`:
   ```html
   <script src="https://unpkg.com/htmx.org/dist/ext/response-targets.js"></script>
   ```
2. Enable it on the parent container using `hx-ext="response-targets"`.
3. Inform HTMX to swap 4xx errors into the target using `hx-target-4xx` (or `hx-target-422`):
   ```html
   <div hx-ext="response-targets">
       <form hx-post="..." hx-target="#form-wrapper" hx-target-4xx="#form-wrapper">
           ...
       </form>
   </div>
   ```

---

## Configuration Reference

You can customize the mixin behavior using the following class attributes:

- `htmx_template_name` *(str)*: Explicitly define the template used for the form fragment.
- `htmx_success_template_name` *(str)*: A template fragment to render when the form is **valid**. Useful if you want to swap the form out for a "Success!" message instead of redirecting.
- `htmx_redirect` *(bool)*: If `True`, a valid form submission will return an `HTTP 204` response with an `HX-Redirect` header pointing to your `success_url`.

## Customization

### Custom HTMX Detection
If you need custom logic to detect an HTMX request, override the `is_htmx()` method:

```python
class MyView(HtmxFormMixin, FormView):
    def is_htmx(self) -> bool:
        # Custom detection logic
        return self.request.headers.get("HX-Request") == "true"
```

### Advanced Success Handling
If `htmx_success_template_name` isn't enough, you can override `form_valid`:

```python
class MyView(HtmxFormMixin, FormView):
    def form_valid(self, form):
        # Do custom stuff
        form.save()
        # Fall back to standard mixin routing
        return super().form_valid(form)
```

## License

MIT License. See `LICENSE` for more information.
