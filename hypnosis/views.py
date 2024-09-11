from django.views.decorators.cache import cache_page

@cache_page(60*60*24*30)
def hypnosis(request):
    from django.shortcuts import render
    return render(request, 'hypnosis/hypnosis.html', {'title': 'Hypnosis', 'hidenavbar': True})
