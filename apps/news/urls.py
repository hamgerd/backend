from django.urls import path

from .feeds import LatestNewsFeed
from .views import NewsDetailAPIView

app_name = "news"

urlpatterns = [
    path("rss/", LatestNewsFeed(), name="news_rss"),
    path("<int:pk>/", NewsDetailAPIView.as_view(), name="news_detail"),
]
