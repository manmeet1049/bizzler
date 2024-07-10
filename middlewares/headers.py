from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse


class HeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = JsonResponse({})
            response["Access-Control-Allow-Origin"] = "*"
            response['Access-Control-Allow-Methods'] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "*"
            return response
        
        response = self.get_response(request)
        if isinstance(response, Response):
            if 'status_code' in response.data:
                status_code = response.data['status_code']
            else:
                status_code = 1 if 200 <= response.status_code < 300 else 0
                
            if 'message' in response.data:
                message = response.data['message']
                response.data.pop('message', None)
            else:
                message = 'success' if status_code==1 else 'failed'
            data = response.data
            standardized_response = {
                "status_code": status_code,
                "message": message,
                "data": data
            }
            
            res=Response(standardized_response, status=response.status_code)
            res.accepted_renderer = JSONRenderer()
            res.accepted_media_type = "application/json"
            res.renderer_context = {}
            res.render()

            res["Access-Control-Allow-Origin"] = "*"
            res["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            res["Access-Control-Allow-Headers"] = "*"
            return res
        
        return response