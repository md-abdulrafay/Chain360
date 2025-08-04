from django import template
from django.contrib.messages import get_messages

register = template.Library()

@register.inclusion_tag('theme/toastify_messages.html', takes_context=True)
def render_toastify_messages(context):
    """
    Render messages as Toastify notifications and consume them from the session
    """
    request = context['request']
    messages = list(get_messages(request))  # This consumes the messages
    return {'messages': messages}
