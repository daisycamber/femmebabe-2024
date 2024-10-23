def process_cart_purchase(user, cart):
    from feed.models import Post
    posts = []
    for item in cart.split(','):
        s = item.split('=')
        uid = s[0]
        quant = s[1]
        post = Post.objects.filter(uuid=uid).first()
        if not p.private:
            if not post.paid_file:
                post.recipient = user
                post.save()
            else:
                post.paid_users.add(user)
                post.save()
        elif p.private and document_scanned(user):
            if not post.paid_file:
                post.recipient = user
                post.save()
            else:
                post.paid_users.add(user)
                post.save()
            posts = posts + [post]
    from feed.email import send_photos_email
    send_photos_email(user, posts)

def get_cart_cost(cookies):
    from feed.models import Post
    items = ''
    try: items = cookies['cart'].split(',') if 'cart' in cookies else []
    except: items = cookies.split(',') if cookies else []
    price = 0
    if len(items) < 1: return 0
    from django.conf import settings
    for item in items[:-1]:
        s = item.split('=')
        uid = s[0]
        quant = 1
        try:
            quant = s[1]
        except: quant = 1
        p = Post.objects.filter(uuid=uid).first()
        price = price + ((int(p.price) * (quant if settings.ALLOW_MULTIPLE_SALES else 1)) if p else 0)
    return price

def get_cart(cookies):
    from feed.models import Post
    items = ''
    try: items = cookies['cart'].split(',') if 'cart' in cookies else []
    except: items = cookies.split(',') if cookies else []
    if len(items) < 1: return None
    contents = ''
    for item in items[:-1]:
        s = item.split('=')
        uid = s[0]
        add = '<button onclick="addToCart(\'{}\');" class="btn btn-outline-success" title="Add another">Add another</button>'.format(uid)
        remove = '<button onclick="removeFromCart(\'{}\');" class="btn btn-outline-danger" title="Remove">Remove</button>'.format(uid)
        quant = 1
        try:
            quant = s[1]
        except: quant = 1
        post = Post.objects.filter(uuid=uid).first()
        if post:
            image = post.get_image_thumb_url() if not post.private else post.get_blur_thumb_url()
            print(uid)
            print(post)
            contents = contents + '<div id="{}"><p>Count: <i id="{}total">{}</i> <img align="left" style="float: left; align: left;" height="100px" width="100px" class="m-2" src="{}">\nOne photo, video, audio, and/or download (<a href="{}" title="See the item">See this item</a>) - ${} ea {}</p><div style="height: 100px;"></div></div>'.format(post.uuid, post.uuid, quant, image, post.get_absolute_url() if post else '', post.price if post else 0, add + ' ' + remove)
    return contents
