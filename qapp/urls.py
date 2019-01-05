from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    url(r'^$', views.IndexView.as_view(), name='gate_list'),
    url(r'^bjc$', views.BjcView.as_view(), name='bjc_list'),
    url(r'^bjw$', views.BjwView.as_view(), name='bjw_list'),
    url(r'^iks$', views.IksView.as_view(), name='iks_list'),
    url(r'^ikk$', views.IkkView.as_view(), name='ikk_list'),
    url(r'^(?P<pk>[\w-]+)/$',
        views.DetailView.as_view(), name='gate_details'),
    url(r'^(?P<pk>[\w-]+)/update$',
        views.gate_update, name='update'),
    url(r'^(?P<pk>[\w-]+)/log$',
        views.LogView.as_view(), name='log'),
    url(r'^add$', views.gate_add, name='gate_add'),
    url(r'^(?P<tram>\D{1}\d{2})/(?P<car>\D{1}\d{1})/(?P<area>\D{3})/(?P<operation_no>\D{2}\d{4})/edit$',
        views.gate_edit, name='edit'),
    #url(r'^(?P<tram>\D{1}\d{2})/(?P<car>\D{1}\d{1})/(?P<area>\D{3})/(?P<operation_no>\D{2}\d{4})/edit$',
        #views.EditGate.as_view(), name='edit'),
    url(r'^mygates$', views.MyGates.as_view(), name='my_gates'),
    url(r'^massupdate$', views.mass_update, name='mass_update')
]