
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static,serve
from django.views.generic.base import RedirectView

from django.urls import path,re_path
import app1.views as a1v
import app2.views as a2v
import app3.views as a3v

urlpatterns = [
    path('admin/', admin.site.urls),

    path('a1', a1v.hello),
    path('a1/t1', a1v.t1),
    path('a1/t2', a1v.t2),
    path('login', a1v.login),
    path('logout', a1v.logout),

    path('a1/list', a1v.select),
    path('a1/del/<int:id>', a1v.delete),
    path('a1/<int:id>/au', a1v.addORupdate),
    path('a1/update', a1v.update),

    path('a2/t1', a2v.t1),
    path('a2/list', a2v.select),
    path('a2/del/<int:id>', a2v.delete),
    path('a2/<int:id>/au', a2v.addORupdate),

    path('a3/list', a3v.select),
    path('a3/del/<int:id>', a3v.delete),
    path('a3/<int:id>/au', a3v.addORupdate),
    path('a3', a3v.home),
    path('a3/ajax', a3v.ajax),

    # re_path(r'a3/re/\d*$', a3v.re_int),
    # re_path(r'a3/re/[A-Za-z]+$', a3v.re_alphabet),
    re_path(r'a3/re/.*$', a3v.re_all),

    path('favicon.ico', RedirectView.as_view(url=r'media/favicon.ico')), 
    # path('favicon.ico', RedirectView.as_view(url=r'static/img/1.jpg')), 

    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root':settings.MEDIA_ROOT},name='media'),

]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
