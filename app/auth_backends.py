from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticate users by e-mail (case-insensitive) while keeping username
    support through the default ModelBackend behavior.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email")
        if email is None and username and "@" in username:
            email = username

        if email:
            user_model = get_user_model()
            email_field = user_model.get_email_field_name()
            try:
                user = user_model._default_manager.get(
                    **{f"{email_field}__iexact": email}
                )
            except user_model.DoesNotExist:
                user_model().set_password(password)
            else:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            return None

        return super().authenticate(request, username=username, password=password, **kwargs)
