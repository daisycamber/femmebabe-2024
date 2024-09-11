def compile(post):
    from django.template.loader import render_to_string
    post.content_compiled = render_to_string('compile.html', {'post': post})
    post.save()