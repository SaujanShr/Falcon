from django import template
from django.contrib.auth.models import Group 

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name): 
    return user.groups.filter(name=group_name).exists()

@register.filter(name='is_staff')
def is_staff(user):
    return has_group(user, 'Admin') or user.is_superuser
