import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

def test_standard_request_fallback(client):
    """A standard non-HTMX request should behave normally and return 200 on failure."""
    url = reverse("standard")
    response = client.post(url, data={})
    
    assert response.status_code == 200
    assert "Full Page" in response.content.decode()

def test_htmx_invalid_form_status_422(client):
    """An invalid HTMX submission should return 422 and swap the partial."""
    url = reverse("standard")
    response = client.post(url, data={}, HTTP_HX_REQUEST="true")
    
    assert response.status_code == 422
    assert "Partial Form" in response.content.decode()
    assert "Full Page" not in response.content.decode()

def test_htmx_valid_form_standard_view(client):
    """A valid HTMX submission with no redirect/success config should behave normally."""
    url = reverse("standard")
    response = client.post(url, data={"name": "Test"}, HTTP_HX_REQUEST="true")
    
    assert response.status_code == 302
    assert response.url == "/success/"

def test_explicit_htmx_template_name(client):
    """If htmx_template_name is set, it should be used instead of auto-resolving."""
    url = reverse("explicit")
    response = client.post(url, data={}, HTTP_HX_REQUEST="true")
    
    assert response.status_code == 422
    assert "Custom Partial" in response.content.decode()

def test_success_template_name(client):
    """If the form is valid and htmx_success_template_name is set, it should return 200 with the success partial."""
    url = reverse("success-template")
    response = client.post(url, data={"name": "John Doe"}, HTTP_HX_REQUEST="true")
    
    assert response.status_code == 200
    assert "Success!" in response.content.decode()

def test_htmx_redirect_header_on_success(client):
    """If htmx_redirect is True, a valid form should return 204 with the HX-Redirect header."""
    url = reverse("redirect")
    response = client.post(url, data={"name": "Alice"}, HTTP_HX_REQUEST="true")
    
    assert response.status_code == 204
    assert response.headers.get("HX-Redirect") == "/redirected/"

def test_is_htmx_with_django_htmx(rf):
    """Test is_htmx detection using django-htmx compatible request attribute."""
    from tests.urls import StandardView
    
    request = rf.post("/standard/", data={})
    # Simulate django-htmx middleware
    request.htmx = True 
    
    view = StandardView(request=request)
    assert view.is_htmx() is True
