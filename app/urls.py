"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django_base_kit.urls import user_urlpatterns

from pairs.views import InvitationSignUpView

from .views import EmailLoginView, HomeView

base_kit_auth_overridden_routes = {"login", "signup"}
base_kit_filtered_routes = [
    route
    for route in user_urlpatterns
    if route.name not in base_kit_auth_overridden_routes
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("accounts/login/", EmailLoginView.as_view(), name="login"),
    path("accounts/signin/", EmailLoginView.as_view(), name="signin"),
    path("accounts/signup/", InvitationSignUpView.as_view(), name="signup"),
    path("", include("accounts.urls")),
    path("", include("pairs.urls")),
    path("", include("reports.urls")),
    path("", include("answers.urls")),
] + base_kit_filtered_routes
