from django import template
from django.contrib.auth.models import Group
from django.conf import settings

register = template.Library()


# filter allow to check that user is in group 'dzj'
@register.filter(name='dzj_member')
def has_group(user):
    group = Group.objects.get(name='dzj')
    return group in user.groups.all()


# filter allow to check that user is in group 'dzj'
@register.filter(name='prod_member')
def has_group(user):
    group = Group.objects.get(name='prod')
    return group in user.groups.all()


# code found on stackoverflow, description below
@register.filter(name='data_verbose')
def data_verbose(bound_field):
    """
    Returns field's data or it's verbose version
    for a field with choices defined.

    Usage::

        {% load data_verbose %}
        {{form.some_field|data_verbose}}
    """
    data = bound_field.data
    field = bound_field.field
    return hasattr(field, 'choices') and dict(field.choices).get(data, '') or data


# filter get attribute of object
@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


# tag allow to paginate filtered results, found on stackoverflow
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
