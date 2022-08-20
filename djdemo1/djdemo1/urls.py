
from django.contrib import admin
from django.urls import path
import app1.views as a1v
import app2.views as a2v

urlpatterns = [
    path('admin/', admin.site.urls),

    path('a1', a1v.hello),
    path('a1/t1', a1v.t1),
    path('a1/t2', a1v.t2),
        path('a1/login', a1v.login),
        path('a1/list', a1v.list),

    path('a2/t1', a2v.t1),

]
