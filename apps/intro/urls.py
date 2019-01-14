from django.conf.urls import url, include
from . import views
app_name = "intro"
urlpatterns = [
<<<<<<< HEAD
    url(r'^$', views.index_2, name='index'),
    url(r'^faq$', views.faq, name='faq'),
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    url(r'^test404/', views.not_found),
    url(r'^staff$', views.staffs),
]

