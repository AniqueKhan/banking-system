from django.contrib.auth.decorators import login_required
from bank_management.models import Notification


@login_required
def count_notifications(request):
    count_notifications = Notification.objects.filter(user=request.user,is_seen=False).count()
    return {"count_notifications":count_notifications}