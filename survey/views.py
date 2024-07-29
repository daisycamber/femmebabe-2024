from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from face.tests import is_superuser_or_vendor
from vendors.tests import is_vendor
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def has_completed_survey(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import SurveyForm, UpdateSurveyForm
    import datetime
    from django.core.paginator import Paginator
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.utils.decorators import method_decorator
    from .models import Survey, Answer
    for s in Survey.objects.all().order_by('priority'):
        a = Answer.objects.filter(survey=s, user=request.user, completed=True)
        if a.count() < 1:
            return HttpResponse('f')
    return HttpResponse('t')

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def survey(request, id):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import SurveyForm, UpdateSurveyForm
    import datetime
    from django.core.paginator import Paginator
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.utils.decorators import method_decorator
    from .models import Survey, Answer
    survey = get_object_or_404(Survey, id=id)
    answer = Answer.objects.filter(user=request.user, survey=survey, completed=False).first()
    if not answer: answer = Answer.objects.create(user=request.user, survey=survey, completed=False)
    answer.user = request.user
    answer.survey = survey
    answer.save()
    if request.method == 'POST':
        form = SurveyForm(survey, request.POST, instance=answer)
        if form.is_valid():
            answer = form.save()
            answer.completed = True
            answer.save()
            for s in Survey.objects.all().order_by('priority'):
                a = Answer.objects.filter(survey=s, user=request.user, completed=True)
                if a.count() < 1:
                    return redirect(reverse('survey:survey', kwargs={'id': s.id}) + '?hidenavbar=t')
            return HttpResponse('You have finished the survey. You will be redirected soon, thank you for your input.')
        else: messages.warning(request, form.errors)
    return render(request, 'survey/survey.html', {
        'form': SurveyForm(survey),
        'full': True
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def answer(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import SurveyForm, UpdateSurveyForm
    import datetime
    from django.core.paginator import Paginator
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.utils.decorators import method_decorator
    from .models import Survey, Answer
    next = request.GET.get('next')
    for s in Survey.objects.all().order_by('priority'):
        a = Answer.objects.filter(survey=s, user=request.user, completed=True)
        if a.count() < 1:
            return render(request, 'survey/answer.html', {
                'title': 'Survey',
                'survey': Survey.objects.all().order_by('priority').first(),
                'full': True
            })
        else: return redirect(next if next else reverse('landing:landing'))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def update(request, id):
    survey = None
    if id != 'new':
        survey = get_object_or_404(Survey, id=id)
    if request.method == 'POST':
        form = UpdateSurveyForm(request.POST, instance=survey)
        if form.is_valid():
            surv = form.save()
            messages.success(request, 'This survey was updated.')
            return redirect(request.path)
    context = {
        'title': 'Update Survey',
        'form': UpdateSurveyForm(instance=survey)
    }
    return render(request, 'survey/update.html', context)

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def surveys(request):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.contrib.auth.models import User
    from users.models import Profile
    from django.contrib import messages
    from .forms import SurveyForm, UpdateSurveyForm
    import datetime
    from django.core.paginator import Paginator
    from django.core.exceptions import PermissionDenied
    from django.http import HttpResponse
    from security.security import fraud_detect
    from django.utils.decorators import method_decorator
    from .models import Survey, Answer
    thesurveys = Survey.objects.all().order_by('priority')
    return render(request, 'survey/surveys.html', {'surveys': thesurveys})
