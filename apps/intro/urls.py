from django.conf.urls import url, include
from django.conf.urls.static import static
from aic_site.settings import base
from . import views
app_name = "intro"
urlpatterns = [
    url(r'^$', views.index_2, name='index'),
    url(r'^faq$', views.faq, name='faq'),
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    #url(r'^test404/', views.not_found),
    url(r'^staff$', views.staffs, name='staff'),
    url(r'^staff-form$', views.staff_form),
    url(r'^staff-add$', views.add_staff, name='add'),
] + static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)

