import django_filters
from .models import Gate, Tram, OperationArea, Bogie
from distutils.util import strtobool
from django import forms


class GateFilter(django_filters.FilterSet):

    # Prepare dynamic lists with choices
    tram_list = [(id, number) for id, number in Tram.objects.all().values_list('id', 'number')]
    bogie_list = [(id, number) for id, number in Bogie.objects.all().values_list('id', 'number')]
    area_list = [(id, area) for id, area in OperationArea.objects.all().values_list('id', 'area')]
    # Generate fields
    tram = django_filters.MultipleChoiceFilter(choices=tram_list, label=u'Tramwaj')
    car = django_filters.MultipleChoiceFilter(choices=Gate.CAR_SYMBOLS, label=u'Człon')
    bogie = django_filters.MultipleChoiceFilter(choices=bogie_list, label=u'Wózek')
    bogie_type = django_filters.MultipleChoiceFilter(choices=Gate.BOGIE_TYPES, label=u'Typ wózka')
    area = django_filters.MultipleChoiceFilter(choices=area_list, label=u'Obszar')
    operation_no = django_filters.CharFilter(label=u'Numer operacji', widget=forms.TextInput(attrs={'size': '16px'}))
    status = django_filters.MultipleChoiceFilter(choices=Gate.GATE_STATUSES, label=u'Status')
    rating = django_filters.MultipleChoiceFilter(choices=Gate.GATE_GRADES, label=u'Ocena')

    class Meta:
        pass

