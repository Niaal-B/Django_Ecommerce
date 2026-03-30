from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class BlockCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only check for authenticated users.
        if request.user.is_authenticated and not request.user.is_active:
            logger.warning(f"Forced logout for blocked user: {request.user.username}")
            logout(request)
            messages.error(request, "Your account has been blocked. Please contact support.")
            return redirect('userlogin')
        
        response = self.get_response(request)
        return response
