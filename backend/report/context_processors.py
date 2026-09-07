def reminder(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"reminder_count": 0}
    from .views import hitung_reminder

    return {"reminder_count": hitung_reminder(user)}
