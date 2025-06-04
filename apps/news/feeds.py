# news/feeds.py

from django.contrib.syndication.views import Feed

from .models import News


class LatestNewsFeed(Feed):
    title = "Latest News"
    link = "/news/rss/"
    description = "Updates on the latest news articles."

    def items(self):
        return News.objects.order_by("-created_at")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return f"https://your-domain.com/news/{item.slug}/"
