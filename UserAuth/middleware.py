from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class BlockCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only check for authenticated users.
        # If the user is authenticated but is_active is False, they were blocked.
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            messages.error(request, "Your account has been blocked. Please contact support.")
            return redirect('userlogin')
        
        response = self.get_response(request)
        return response
