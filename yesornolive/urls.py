"""yesornolivebeta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.shortcuts import render, render_to_response

from django.template import RequestContext
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from general.views import homepage
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete



def server_error(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response

#page not found
def custom_404(request):
    response = render(request, "404.html")
    response.status_co


urlpatterns = [

    
    url(r'^adminYnl/', admin.site.urls),
    url(r'^', include("general.urls", namespace="general")),
    url(r'^backend/', include("ynladmin.urls", namespace="ynladmin")),
    url(r'^', include("wallet.urls", namespace="wallet")),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    #url(r'^tinymce/', include('tinymce.urls', namespace='tinymce')),
    url(r'^game/', include('gameplay.urls', namespace="gameplay")),

    url(r'^mobile-validator-api/', include('mobileValidator.urls')),
    
    #change password urls
    url(r'^reset/form/$', TemplateView.as_view(template_name = 'registration/password_reset_email.html')),
    url(r'^resetpassword/passwordsent/$', password_reset_done, name="password_reset_done"),
    url(r'^resetpassword/$', password_reset, name="password_reset"),
    # url(r'^resetpassword/$', custom_password_reset, name="password_reset"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name="password_reset_confirm"),
    url(r'^reset/done/$', password_reset_complete, name="password_reset_complete"),


]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
