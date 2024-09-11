def post_ai_response(user, text):
    from feed.models import Post
    from django.conf import settings
    post, created = Post.objects.get_or_create(posted=True, published=True, public=True, private=False, feed=settings.VOICE_FEED, author=user, content=text)
    post.save()

def get_ai_response(text):
    from openai import OpenAI
    from django.conf import settings
    client = OpenAI(api_key=settings.OPENAI_KEY)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content
