def user_tasks(user_is_authenticated, user_id, ip, language_code):
    from django.contrib.auth.models import User
    user = User.objects.filter(id=user_id).first()
    if not user or not user_is_authenticated: return
    from django.shortcuts import get_object_or_404
    from users.models import Profile
    from django.utils import timezone
    from voice.models import VoiceProfile
    from django.conf import settings
    import traceback
    if user_is_authenticated and hasattr(user, 'profile'):
        user = get_object_or_404(User, pk=user.pk)
        # Update last visit time after request finished processing.
        user.profile.last_seen = timezone.now()
        try:
            user.profile.language_code = language_code
        except: user.profile.language_code = settings.DEFAULT_LANG
        last_ip = user.profile.ip
        user.profile.ip = ip
        try:
            user.profile.save()
        except:
            print(traceback.format_exc())
        if user.profile.identity_verified:
            if not hasattr(user, 'voice_profile'):
                voice_profile = VoiceProfile.objects.create(user=user)
                voice_profile.save()
    elif not hasattr(user, 'profile') and isinstance(user, User):
        p = Profile()
        p.email_verified = True
        p.user = user
        p.save()

