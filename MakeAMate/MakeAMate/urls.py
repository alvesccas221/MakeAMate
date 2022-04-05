"""MakeAMate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
#from turtle import home
from django.contrib import admin
from django.urls import path, include
from principal import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf.urls import handler404,handler403,handler500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login_view,name="login"),
    path("logout/", views.logout_view, name= "logout"),
    path("accept-mate/", views.accept_mate, name= "accept-mate"),
    path("reject-mate/", views.reject_mate, name= "reject-mate"),
    path("payments/",views.payments,name="payments"),
    path("notifications/",views.notifications_list,name="notifications"),
    path("info/",views.info,name="info"),
    path('', views.homepage,name="home"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
    path('chat/',include('chat.urls')),
]

handler403 = "principal.views.error_403"
handler404 = "principal.views.error_404"
handler500 = "principal.views.error_500"