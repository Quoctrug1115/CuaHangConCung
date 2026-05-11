class PermissionsPolicyMiddleware:
    """
    Thêm header Permissions-Policy để cho phép Geolocation API
    hoạt động trên tất cả browsers kể cả khi có restrictive policy.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Cho phép geolocation từ same-origin
        response['Permissions-Policy'] = 'geolocation=(self)'
        # Referrer policy để OSM tile không bị block
        response['Referrer-Policy'] = 'no-referrer-when-downgrade'
        return response
