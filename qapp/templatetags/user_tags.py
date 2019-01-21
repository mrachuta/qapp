from django import template
from django.contrib.auth.models import Group
from django.conf import settings

register = template.Library()


@register.filter(name='dzj_member')
def has_group(user):
    group = Group.objects.get(name='dzj')
    return group in user.groups.all()


@register.filter(name='prod_member')
def has_group(user):
    group = Group.objects.get(name='prod')
    return group in user.groups.all()


@register.filter(name='data_verbose')
def data_verbose(boundField):
    """
    Returns field's data or it's verbose version
    for a field with choices defined.

    Usage::

        {% load data_verbose %}
        {{form.some_field|data_verbose}}
    """
    data = boundField.data
    field = boundField.field
    return hasattr(field, 'choices') and dict(field.choices).get(data,'') or data

@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)

