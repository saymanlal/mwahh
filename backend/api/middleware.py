import os
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}

    def __call__(self, request):
        from django.core.cache import cache

        client_ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{client_ip}'
        
        request_count = cache.get(cache_key, 0)
        
        if request_count >= 100:
            logger.warning(f'Rate limit exceeded for {client_ip}')
            return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
        
        cache.set(cache_key, request_count + 1, 60)
        
        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if os.environ.get('DEBUG') != 'True':
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
            return JsonResponse(
                {'error': 'Internal server error'},
                status=500
            )
