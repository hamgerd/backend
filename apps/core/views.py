from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class HealthCheckAPI(APIView):
    """
    A Health check API to 
    monitor service availability
    """
    def get(self, request):
        """ Only listen on GET method """
        return Response({"status": "success"}, status=status.HTTP_200_OK)
