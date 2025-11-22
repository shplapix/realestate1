from .models import Message

def unread_messages_count(request):
    count = 0
    if request.user.is_authenticated:
        if hasattr(request.user, 'realtor'):
            # User is a realtor, count messages from buyers (is_realtor_sender=False)
            count = Message.objects.filter(
                chat__realtor=request.user.realtor,
                is_realtor_sender=False,
                is_read=False
            ).count()
        else:
            # User is a buyer, count messages from realtors (is_realtor_sender=True)
            count = Message.objects.filter(
                chat__user=request.user,
                is_realtor_sender=True,
                is_read=False
            ).count()
            
    return {'unread_messages_count': count}
