from .models import Gate
from django.db.models import Q


def get_most_rejected(request):

    topfive = Gate.objects.all().filter(~Q(gate_status='A')).filter(~Q(reject_counter=0)).order_by('-reject_counter')[:5]

    return {
        'topfive': topfive
    }