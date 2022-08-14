
from django.contrib import admin
from django.urls import path
from djdemo1.app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello', views.hello),
]