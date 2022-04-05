from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.paypal ,name='paypal' ),
    path('completed/', views.paymentComplete, name="complete"),
    path('home/',views.homepageRedirect,name="home")


]