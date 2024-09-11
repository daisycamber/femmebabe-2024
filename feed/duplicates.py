
def remove_post_duplicates():
    import hashlib, os
    from feed.models import Post
    from lotteh.celery import delay_delete_post
    duplicates = []
    hash_keys = dict()
    for post in Post.objects.all().order_by('date_posted'):
        if not post.image_hash and post.image and post.image_original and os.path.isfile(post.image_original.path):
            with open(post.image_original.path, 'rb') as f:
                filehash = hashlib.md5(f.read()).hexdigest()
            if not filehash in hash_keys:
                hash_keys[filehash] = post.id
            else:
                duplicates.append(post.id)
        elif post.image_hash:
            if not post.image_hash in hash_keys:
                hash_keys[post.image_hash] = post.id
            else:
                duplicates.append(post.id)
    for d in duplicates:
        post = Post.objects.get(id=d)
        post.private = True
        post.published = False
        post.save()
        delay_delete_post.apply_async([d], countdown=60*2)
