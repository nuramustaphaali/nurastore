from django.shortcuts import render

def index(request):
    """
    Renders the Single Page Application (SPA) shell.
    Data will be fetched via JS from the API later.
    """
    return render(request, 'web/index.html')