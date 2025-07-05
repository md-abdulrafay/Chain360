from .views import get_notifications

def notifications(request):
    return {'notifications': get_notifications()}
