def patch_users(alternate_db):
    from django.contrib.auth.models import User
    for user in User.objects.all():
        if not User.objects.using(alternate_db).filter(id=user.id):
            user.save(using=alternate_db)
