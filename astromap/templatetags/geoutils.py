from django import template
from astromap import utils

register = template.Library()

@register.filter('deg2hms')
def deg2hms(val):
    return utils.deg2hms(val)
