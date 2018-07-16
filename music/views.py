from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'music/home.html', {'test_context': 'Sagar'})
