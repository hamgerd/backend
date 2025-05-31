# views.py

from rest_framework.generics import RetrieveAPIView
from .models import News
from .serializers import NewsSerializer

class NewsDetailAPIView(RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
