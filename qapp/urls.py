from . import views
from django.conf.urls import url

"""
For using one generic.ListView for all type of gates, is necessary to specify parameter gate_type in as_view method.
This parameter will be provided to Class GateListView in views.py and available in each method of this class.
"""

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^bjc$', views.GateListView.as_view(gate_type='bjc'), name='bjc_list'),
    url(r'^bjw$', views.GateListView.as_view(gate_type='bjw'), name='bjw_list'),
    url(r'^ikw$', views.GateListView.as_view(gate_type='ikw'), name='ikw_list'),
    url(r'^ikk$', views.GateListView.as_view(gate_type='ikk'), name='ikk_list'),
    url(r'^(?P<pk>[\w-]+)/$', views.DetailView.as_view(), name='gate_details'),
    url(r'^(?P<pk>[\w-]+)/update$', views.gate_update, name='update'),
    url(r'^(?P<pk>[\w-]+)/log$', views.LogView.as_view(), name='log'),
    url(r'^add$', views.gate_add, name='gate_add'),
    url(r'^(?P<pk>[\w-]+)/edit$', views.gate_edit, name='edit'),
    url(r'^mygates$', views.MyGates.as_view(), name='my_gates'),
    url(r'^massupdate$', views.mass_update, name='mass_update'),
    url(
        r'^csm/(?P<car>\D\d)/(?P<operation_no>\D{2}\d{4})$',
        views.gate_change_status_mobile,
        name='gate_change_status_mobile'
    )

]
