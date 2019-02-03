from .models import Gate
from django.db.models import Q


def get_most_rejected(request):

    topfive = Gate.objects.all().filter(~Q(gate_status='A')).filter(~Q(reject_counter=0)).order_by('-reject_counter')[:5]

    return {
        'topfive': topfive
    }


def get_latest_count(request):

    if request.user.groups.filter(name='dzj').exists():
        user_gates_count = Gate.objects.all().filter(author=request.user, gate_status='O').order_by('tram').count()
    else:
        user_gates_count = Gate.objects.all().filter(area__responsible=request.user, gate_status='P').order_by('tram').count()

    return {
        'user_gates_count': user_gates_count
    }
