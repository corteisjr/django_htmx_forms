from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from django.http import HttpResponse, HttpRequest
from django.template.response import TemplateResponse


class HtmxFormMixin:
    """
    Mixin for Django class-based form views to swap the form fragment
    on HTMX requests and avoid full page reloads on validation errors.

    Usage:
        class ContactView(HtmxFormMixin, FormView):
            template_name = "contact/page.html"
            success_url = "/thanks/"
    """

    htmx_template_name: str | None = None
    htmx_success_template_name: str | None = None
    htmx_redirect: bool = False
    request: HttpRequest

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]: ...
    def get_success_url(self) -> str: ...

    def is_htmx(self) -> bool:
        request = self.request
        htmx = getattr(request, "htmx", None)
        if htmx is not None:
            return bool(htmx)
        return request.headers.get("HX-Request") == "true"

    def _derive_htmx_candidates(self, template_name: str) -> list[str]:
        path = PurePosixPath(template_name)
        if not path.name:
            return []
        return [
            str(path.with_name("_form.html")),
            str(path.with_name(f"_{path.name}")),
        ]

    def get_template_names(self) -> list[str]:
        return super().get_template_names()  # type: ignore[misc]

    def get_htmx_template_names(self, *, success: bool = False) -> list[str]:
        if success and self.htmx_success_template_name:
            return [self.htmx_success_template_name]
        if self.htmx_template_name:
            return [self.htmx_template_name]

        base_names = self.get_template_names()
        candidates: list[str] = []
        for name in base_names:
            candidates.extend(self._derive_htmx_candidates(name))
        candidates.extend(base_names)

        seen: set[str] = set()
        deduped: list[str] = []
        for name in candidates:
            if name in seen:
                continue
            seen.add(name)
            deduped.append(name)
        return deduped

    def _render_htmx_response(
        self, *, form: Any, success: bool = False, status: int | None = None
    ) -> TemplateResponse:
        context = self.get_context_data(form=form)
        template_names = self.get_htmx_template_names(success=success)
        response = TemplateResponse(
            self.request,
            template_names,
            context,
        )
        if status is not None:
            response.status_code = status
        return response

    def form_invalid(self, form: Any) -> HttpResponse:
        if self.is_htmx():
            return self._render_htmx_response(form=form, success=False, status=422)
        return super().form_invalid(form)  # type: ignore[misc]

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)  # type: ignore[misc]
        if not self.is_htmx():
            return response

        if self.htmx_success_template_name:
            return self._render_htmx_response(form=form, success=True)

        if self.htmx_redirect and hasattr(self, "get_success_url"):
            redirect_response = HttpResponse(status=204)
            redirect_response["HX-Redirect"] = self.get_success_url()
            return redirect_response

        return response
