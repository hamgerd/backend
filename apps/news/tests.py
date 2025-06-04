from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import News


class NewsFeedTest(TestCase):
    def setUp(self):
        self.news1 = News.objects.create(
            title="Test News 1", content="Content for test news 1", created_at=timezone.now()
        )
        self.news2 = News.objects.create(
            title="Test News 2", content="Content for test news 2", created_at=timezone.now()
        )

    def test_rss_feed_status_code(self):
        url = reverse("news:news_rss")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rss_feed_contains_news_titles(self):
        url = reverse("news:news_rss")
        response = self.client.get(url)
        self.assertContains(response, self.news1.title)
        self.assertContains(response, self.news2.title)

    def test_rss_feed_is_xml(self):
        url = reverse("news:news_rss")
        response = self.client.get(url)
        self.assertEqual(response["Content-Type"], "application/rss+xml; charset=utf-8")
