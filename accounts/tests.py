# accounts/tests.py
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponse, HttpResponseRedirect
from unittest.mock import patch
import accounts.views as views

User = get_user_model()

# Helper functions to prepare request objects

def attach_session(request):
    """Attach a session to the request so login/logout functions work."""
    mw = SessionMiddleware(lambda r: None)
    mw.process_request(request)
    request.session.save()
    return request

def attach_messages(request):
    """Attach a message storage backend to the request for messages.success/error."""
    setattr(request, "_messages", FallbackStorage(request))
    return request

# Dummy and Spy form classes to mock form behavior

class DummyRegisterForm:
    """Valid registration form that creates a test user."""
    def __init__(self, *args, **kwargs): pass
    def is_valid(self): return True
    def save(self):
        return User.objects.create_user(
            email="john@example.com",
            password="secret123"
        )

class DummyRegisterFormInvalid:
    """Invalid registration form that simulates validation errors."""
    def __init__(self, *args, **kwargs): self.errors = {"email": ["invalid"]}
    def is_valid(self): return False

class DummyLoginFormSimple:
    """Valid login form returning a specific user for form_valid tests."""
    def __init__(self, user_obj): self._user = user_obj
    def is_valid(self): return True
    def get_user(self): return self._user

class DummyLoginFormInvalid:
    """Invalid login form to trigger form_invalid behavior."""
    def __init__(self, *args, **kwargs): pass
    def is_valid(self): return False

class DummyProfileFormValid:
    """Valid profile update form that saves successfully."""
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance")
    def is_valid(self): return True
    def save(self): return self.instance

class DummyProfileFormInvalid:
    """Invalid profile update form to simulate errors."""
    def __init__(self, *args, **kwargs):
        self.errors = {"field": ["Invalid"]}
    def is_valid(self): return False

class SpyProfileForm:
    """Spy form to check if instance=request.user is passed in GET requests."""
    last_instance = None
    def __init__(self, *args, **kwargs):
        SpyProfileForm.last_instance = kwargs.get("instance")
    def is_valid(self): return True
    def save(self): return self

class DummyPasswordChangeForm:
    """Valid password change form with a new password in cleaned_data."""
    cleaned_data = {"new_password": "new-strong-pass-123"}
    def is_valid(self): return True

class DummyPasswordChangeFormInvalid:
    """Invalid password change form to trigger form_invalid."""
    def __init__(self, *args, **kwargs): pass
    def is_valid(self): return False


class ViewsTests(TestCase):
    """Unit and integration tests for accounts.views."""

    def setUp(self):
        self.factory = RequestFactory()

    # RegisterView tests

    def test_register_view_invalid_renders(self):
        """Invalid registration form returns HTTP 200 with rendered template."""
        req = self.factory.post("/accounts/register/", data={})
        req = attach_session(req)
        req.user = AnonymousUser()
        with patch.object(views.RegisterView, "form_class", DummyRegisterFormInvalid), \
                patch.object(views.RegisterView, "template_name", "accounts/register.html"):
            resp = views.RegisterView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_register_sets_correct_user_in_session(self):
        """After successful registration, the new user's ID is stored in the session."""
        req = self.factory.post("/accounts/register/", data={})
        req = attach_session(req); req.user = AnonymousUser()
        with patch.object(views.RegisterView, "form_class", DummyRegisterForm), \
             patch.object(views.RegisterView, "success_url", "/"):
            views.RegisterView.as_view()(req)
        created = User.objects.get(email="john@example.com")
        self.assertEqual(str(created.pk), req.session.get("_auth_user_id"))

    # LoginView tests

    def test_login_view_logs_in_and_redirects(self):
        """Valid login form logs the user in and redirects."""
        user = User.objects.create_user(email="maria@example.com", password="pass12345")
        req = self.factory.post("/accounts/login/", data={})
        req = attach_session(req); req.user = AnonymousUser()
        view = views.LoginView(); view.request = req
        with patch.object(views.LoginView, "success_url", "/"):
            resp = view.form_valid(DummyLoginFormSimple(user))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")
        self.assertIn("_auth_user_id", req.session)

    def test_login_view_invalid_renders(self):
        """Invalid login form returns HTTP 200 with rendered template."""
        req = self.factory.post("/accounts/login/", data={})
        req = attach_session(req); req.user = AnonymousUser()
        with patch.object(views.LoginView, "form_class", DummyLoginFormInvalid), \
             patch.object(views.LoginView, "template_name", "accounts/login.html"):
            resp = views.LoginView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    # logout_view tests

    def test_logout_view_clears_session_and_redirects(self):
        """Logged-in user is logged out and redirected."""
        user = User.objects.create_user(email="peter@example.com", password="pass123")
        req = self.factory.get("/accounts/logout/")
        req = attach_session(req); req.user = user
        with patch.object(views, "redirect", side_effect=lambda to: HttpResponseRedirect("/")):
            resp = views.logout_view(req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")
        self.assertNotIn("_auth_user_id", req.session)

    def test_logout_view_anonymous_still_redirects(self):
        """Anonymous user hitting logout still gets redirected."""
        req = self.factory.get("/accounts/logout/")
        req = attach_session(req); req.user = AnonymousUser()
        with patch.object(views, "redirect", side_effect=lambda to: HttpResponseRedirect("/")):
            resp = views.logout_view(req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")

    # profile_update tests

    def test_profile_update_get_renders_form(self):
        """GET request to profile_update renders form with user instance."""
        user = User.objects.create_user(email="anna@example.com", password="qwerty123")
        req = self.factory.get("/accounts/profile/")
        req = attach_session(req); req = attach_messages(req); req.user = user
        with patch.object(views, "render", return_value=HttpResponse("OK")) as m_render:
            resp = views.profile_update(req)
        self.assertEqual(resp.status_code, 200)
        args, kwargs = m_render.call_args
        ctx = args[2] if len(args) >= 3 else kwargs.get("context", {})
        self.assertIn("form", ctx)

    def test_profile_update_get_uses_instance_user(self):
        """Form instance should be the logged-in user on GET."""
        user = User.objects.create_user(email="eva@example.com", password="pw12345")
        req = self.factory.get("/accounts/profile/")
        req = attach_session(req); req = attach_messages(req); req.user = user
        with patch.object(views, "UserProfileForm", SpyProfileForm), \
             patch.object(views, "render", return_value=HttpResponse("OK")):
            views.profile_update(req)
        self.assertEqual(SpyProfileForm.last_instance, user)

    def test_profile_update_post_valid_redirects_and_message(self):
        """Valid POST updates profile, adds success message, and redirects."""
        user = User.objects.create_user(email="kate@example.com", password="qwerty123")
        req = self.factory.post("/accounts/profile/", data={"first_name": "Kate"})
        req = attach_session(req); req = attach_messages(req); req.user = user
        with patch.object(views, "UserProfileForm", DummyProfileFormValid), \
             patch.object(views, "redirect", side_effect=lambda to: HttpResponseRedirect("/")):
            resp = views.profile_update(req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")
        self.assertTrue(any(m.level_tag == "success" for m in list(req._messages)))

    def test_profile_update_post_invalid_renders_with_error_message(self):
        """Invalid POST shows error message and re-renders form."""
        user = User.objects.create_user(email="tom@example.com", password="qwerty123")
        req = self.factory.post("/accounts/profile/", data={"bad": "data"})
        req = attach_session(req); req = attach_messages(req); req.user = user
        with patch.object(views, "UserProfileForm", DummyProfileFormInvalid), \
             patch.object(views, "render", return_value=HttpResponse("ERR")) as m_render:
            resp = views.profile_update(req)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(m.level_tag == "error" for m in list(req._messages)))
        m_render.assert_called()

    def test_profile_update_requires_login(self):
        """Anonymous user accessing profile_update is redirected to login."""
        req = self.factory.get("/accounts/profile/")
        req = attach_session(req); req.user = AnonymousUser()
        resp = views.profile_update(req)
        self.assertEqual(resp.status_code, 302)

    # PasswordChangeView tests

    def test_password_change_updates_password_and_keeps_logged_in(self):
        """Valid password change updates password and keeps user logged in."""
        user = User.objects.create_user(email="zara@example.com", password="oldpass123")
        req = self.factory.post("/accounts/password-change/", data={"new_password": "x"})
        req = attach_session(req); req.user = user
        view = views.PasswordChangeView(); view.request = req
        with patch.object(views.PasswordChangeView, "form_class", DummyPasswordChangeForm), \
             patch.object(views.PasswordChangeView, "success_url", "/"):
            resp = view.form_valid(DummyPasswordChangeForm())
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")
        user.refresh_from_db()
        self.assertTrue(user.check_password("new-strong-pass-123"))
        self.assertFalse(user.check_password("oldpass123"))
        self.assertIn("_auth_user_id", req.session)

    def test_password_change_requires_login(self):
        """Anonymous user is redirected when trying to access PasswordChangeView."""
        req = self.factory.get("/accounts/password-change/")
        req = attach_session(req); req.user = AnonymousUser()
        resp = views.PasswordChangeView.as_view()(req)
        self.assertEqual(resp.status_code, 302)

    def test_password_change_invalid_form_renders(self):
        """Invalid password change form returns HTTP 200 with rendered template."""
        user = User.objects.create_user(email="neal@example.com", password="abc12345")
        req = self.factory.post("/accounts/password-change/", data={"new_password": ""})
        req = attach_session(req); req.user = user
        with patch.object(views.PasswordChangeView, "form_class", DummyPasswordChangeFormInvalid), \
             patch.object(views.PasswordChangeView, "template_name", "accounts/password_change.html"):
            resp = views.PasswordChangeView.as_view()(req)
        self.assertEqual(resp.status_code, 200)
