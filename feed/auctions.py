def update_auctions():
    from feed.models import Post
    from django.utils import timezone
    for post in Post.objects.filter(date_auction__gte=timezone.now(), date_auction__lte=timezone.now()+datetime.timedelta(days=1)):
        if post.bids.count():
            post.price = str(post.bids.last().bid)
            post.save()
            u = post.bids.last().user
            from feed.views import sub_fee
            from django.conf import settings
            from users.email import send_user_email
            send_user_email(post.author, 'Your auction has been won by {}'.format(u.username), 'Congratulations! Your auction for {} has been won by {} on {}. This auction\'s total was ${}'.format(post.friendly_name, u.username, settings.SITE_NAME, sub_fee(post.bids.last().bid)))
            send_user_email(post.bids.last().user, 'You won an auction on {}, @{}'.format(settings.BASE_URL, u.username), 'Congratulations! Your auction for {} has been won by {} on {}. This auction\'s total was ${}. You can pay for the auction by <a href="{}/feed/post/{}/" title="Click here to pay">clicking here</a> or by pasting the link below into your navbar.\n\n{}\n\nOnce again, thank you for your bid!'.format(post.friendly_name, u.username, settings.SITE_NAME, sub_fee(post.bids.last().bid), settings.BASE_URL, post.friendly_name, settings.BASE_URL, post.friendly_name))
