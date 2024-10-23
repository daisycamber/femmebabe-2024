from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

MIN_CONSTELLATION = 6
MIN_SCORE = 0.2

def validate_score(user, instance):
    from .forms import MelaninPhotoForm
    from .models import MelaninPhoto
    from django.shortcuts import render, redirect
    from django.urls import reverse
    from melanin.kabsch import validate_melanin_images
    score = 0.0
    photos = MelaninPhoto.objects.filter(user=user).order_by('-timestamp')
    for photo in photos:
        score = score + 1.0 if validate_melanin_images(photo.image.path, instance.image.path) else 0.0
    score = (score * 1.0)/photos.count()
    return score

@csrf_exempt
@login_required
def melanin(request):
    from .forms import MelaninPhotoForm
    from .models import MelaninPhoto
    from django.shortcuts import render, redirect
    from django.urls import reverse
    if request.method == 'POST':
        form = MelaninPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            instance = form.save()
            photos = MelaninPhoto.objects.filter(user=request.user).order_by('-timestamp')[:16]
            from melanin.contours import get_image_contours
            valid = False
            if photos.count() == 1 and len(get_image_contours(instance.image.path)) >= MIN_CONSTELLATION:
                valid = True
            elif photos.count() > 1 and validate_score(request.user, instance) > MIN_SCORE:
                valid = True
            if valid: return redirect(reverse('go:go') if not request.GET.get('next') else request.GET.get('next'))
            else: instance.delete()
    return render(request, 'melanin/melanin.html', {'title': 'Validate Constellation', 'form': MelaninPhotoForm()})
