from .models import Gate
from django.db.models import Q


def get_most_rejected(request):

    # Provide list of five gates with biggest reject-counter. Available on all templates.

    queryset = Gate.objects.all().filter(~Q(status='A')).filter(~Q(reject_counter=0)).order_by('-reject_counter')
    top_five = queryset[:5]
    return {
        'top_five': top_five
    }


def get_latest_count(request):

    # Provide counter for authenticated user.
    # For 'dzj' group member: providing counter of pending to inspection Gate(s);
    # for rest of users: providing counter of rejected (need to be fixed) Gate(s).
    # Available on all templates.

    if request.user.is_authenticated:
        if request.user.groups.filter(name='dzj').exists():
            user_gates_count = Gate.objects.all().\
                filter(author=request.user, status='O').order_by('tram').count()
        else:
            user_gates_count = Gate.objects.all().\
                filter(responsible=request.user, status='P').order_by('tram').count()
        return {
            'user_gates_count': user_gates_count
        }
    else:
        return {
            'user_gates_count': 'Not available'
        }
