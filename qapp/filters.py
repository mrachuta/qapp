import django_filters
from django import forms
from .models import Gate, Tram, OperationArea, Bogie


class GateFilter(django_filters.FilterSet):

    # Generate fields
    tram = django_filters.ModelMultipleChoiceFilter(queryset=Tram.objects.all().order_by('-number'), label=u'Tramwaj')
    car = django_filters.MultipleChoiceFilter(choices=Gate.CAR_SYMBOLS, label=u'Człon')
    bogie = django_filters.ModelMultipleChoiceFilter(queryset=Bogie.objects.all().order_by('-number'), label=u'Wózek')
    area = django_filters.ModelMultipleChoiceFilter(queryset=OperationArea.objects.all(), label=u'Obszar')
    operation_no = django_filters.CharFilter(label=u'Numer operacji', widget=forms.TextInput(attrs={'size': '16px'}))
    status = django_filters.MultipleChoiceFilter(choices=Gate.GATE_STATUSES, label=u'Status')
    rating = django_filters.MultipleChoiceFilter(choices=[(id, id) for id, value in Gate.GATE_GRADES], label=u'Ocena')

    class Meta:
        pass

