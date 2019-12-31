from django.shortcuts import render
from django.http import HttpResponse
from .models import Tutorial, TutorialCategory, TutorialSeries
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages




# Create your views here.

def single_slug(request, single_slug):
    categories = [c.category_slug for c in TutorialCategory.objects.all()]
    if single_slug in categories:
        matching_series = TutorialSeries.objects.filter(tutorial_category__category_slug = single_slug)
        
        series_urls = {}
        for m in matching_series.all():
            part_one = Tutorial.objects.filter(tutorial_series__tutorial_series = m.tutorial_series).earliest("tutorial_published")
            series_urls[m] = part_one.tutorial_slug
 
        return render(request,
                        "main/category.html",
                        {"part_ones": series_urls})


    tutorials = [t.tutorial_slug for t in Tutorial.objects.all()]
    if single_slug in tutorials:
        this_tutorial = Tutorial.objects.get(tutorial_slug = single_slug)
        tutorials_from_series = Tutorial.objects.filter(tutorial_series__tutorial_series=this_tutorial.tutorial_series).order_by("tutorial_published")
        
        this_tutorial_idx = list(tutorials_from_series).index(this_tutorial)

        return render(request,
                      "main/tutorial.html",
                       {"tutorial": this_tutorial,
                        "sidebar": tutorials_from_series,
                        "this_tutorial_idx": this_tutorial_idx})
                       

    return HttpResponse(f"{single_slug} soes not correspond to anything")



def homepage(request): 
    return render(request = request,
                  template_name='main/categories.html',
                  context = {"categories":TutorialCategory.objects.all})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New User Created: {username}")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                          template_name = "main/register.html",
                          context={"form":form})

    form = UserCreationForm
    return render(request = request,
                  template_name = "main/register.html",
                  context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect("main:homepage")

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                messages.info(request, f"you are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request,"Invalid username of password.")
    form = AuthenticationForm()
    return render(request=request,
                  template_name = "main/login.html",
                  context={"form":form})


