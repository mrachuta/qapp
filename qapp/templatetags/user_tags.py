from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='dzj_member')
def has_group(user):
    group = Group.objects.get(name='dzj')
    return group in user.groups.all()


@register.filter(name='prod_member')
def has_group(user):
    group = Group.objects.get(name='prod')
    return group in user.groups.all()