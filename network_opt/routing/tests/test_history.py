from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from routing.models import Node, RouteHistory


class RouteHistoryAPITestCase(TestCase):
    """Test Route history query endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/routes/history/'

        # Setup nodes
        self.node_a = Node.objects.create(name='ServerA')
        self.node_b = Node.objects.create(name='ServerB')
        self.node_c = Node.objects.create(name='ServerC')
        self.node_d = Node.objects.create(name='ServerD')

    def test_get_history_all(self):
        """GET /routes/history - List all history records."""
        now = timezone.now()
        RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD'],
            created_at=now
        )
        RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC'],
            created_at=now
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_history_filter_by_source(self):
        """GET /routes/history?source=ServerA - Filter by source."""
        now = timezone.now()
        RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD'],
            created_at=now
        )
        RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC'],
            created_at=now
        )

        response = self.client.get(f'{self.url}?source=ServerA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source'], 'ServerA')

    def test_get_history_filter_by_destination(self):
        """GET /routes/history?destination=ServerD - Filter by destination."""
        now = timezone.now()
        RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD'],
            created_at=now
        )
        RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC'],
            created_at=now
        )

        response = self.client.get(f'{self.url}?destination=ServerD')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['destination'], 'ServerD')

    def test_get_history_filter_by_source_and_destination(self):
        """GET /routes/history?source=ServerA&destination=ServerD - Filter both."""
        now = timezone.now()
        RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD'],
            created_at=now
        )
        RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_b,
            total_latency=12.5,
            path=['ServerA', 'ServerB'],
            created_at=now
        )

        response = self.client.get(f'{self.url}?source=ServerA&destination=ServerD')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['destination'], 'ServerD')

    def test_get_history_filter_by_limit(self):
        """GET /routes/history?limit=1 - Limit results."""
        now = timezone.now()
        RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD'],
            created_at=now
        )
        RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC'],
            created_at=now
        )

        response = self.client.get(f'{self.url}?limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_history_filter_by_date_from(self):
        """GET /routes/history?date_from=ISO - Filter by start date."""
        now = timezone.now()
        old_date = now - timedelta(days=5)
        future_date = now + timedelta(days=1)

        r1 = RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD']
        )
        r1.created_at = old_date
        r1.save(update_fields=['created_at'])

        r2 = RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC']
        )
        r2.created_at = future_date
        r2.save(update_fields=['created_at'])

        response = self.client.get(f'{self.url}?date_from={future_date.isoformat()}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source'], 'ServerB')

    def test_get_history_filter_by_date_to(self):
        """GET /routes/history?date_to=ISO - Filter by end date."""
        now = timezone.now()
        old_date = now - timedelta(days=5)

        r1 = RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD']
        )
        r1.created_at = old_date
        r1.save(update_fields=['created_at'])

        r2 = RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC']
        )
        r2.created_at = now
        r2.save(update_fields=['created_at'])

        response = self.client.get(f'{self.url}?date_to={old_date.isoformat()}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source'], 'ServerA')

    def test_get_history_combined_filters(self):
        """GET /routes/history?source=X&limit=N&date_from=ISO - Combined filters."""
        now = timezone.now()
        old_date = now - timedelta(days=5)

        r1 = RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_d,
            total_latency=23.4,
            path=['ServerA', 'ServerB', 'ServerD']
        )
        r1.created_at = old_date
        r1.save(update_fields=['created_at'])

        r2 = RouteHistory.objects.create(
            source=self.node_a,
            destination=self.node_b,
            total_latency=12.5,
            path=['ServerA', 'ServerB']
        )
        r2.created_at = now
        r2.save(update_fields=['created_at'])

        r3 = RouteHistory.objects.create(
            source=self.node_b,
            destination=self.node_c,
            total_latency=10.1,
            path=['ServerB', 'ServerC']
        )
        r3.created_at = now
        r3.save(update_fields=['created_at'])

        response = self.client.get(f'{self.url}?source=ServerA&limit=1&date_from={now.isoformat()}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source'], 'ServerA')
        self.assertEqual(response.data[0]['destination'], 'ServerB')
