from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define URLs that don't require authentication
        open_urls = [reverse('login'), reverse('register'), reverse('logout')]
        
        # Check if user is authenticated for protected URLs
        if not request.user.is_authenticated and request.path not in open_urls and not request.path.startswith('/admin/'):
            return redirect(f'{reverse("login")}?next={request.path}')
        
        response = self.get_response(request)
        return response