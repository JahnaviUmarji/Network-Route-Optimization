from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from routing.models import Node, Edge, RouteHistory


class RouteAPITestCase(TestCase):
    """Test Route shortest path endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/routes/shortest/'

        # Setup nodes
        self.node_a = Node.objects.create(name='ServerA')
        self.node_b = Node.objects.create(name='ServerB')
        self.node_c = Node.objects.create(name='ServerC')
        self.node_d = Node.objects.create(name='ServerD')

    def test_shortest_route_success(self):
        """POST /routes/shortest - Find shortest path."""
        # A -> B (12.5), B -> D (10.9)
        Edge.objects.create(source=self.node_a, destination=self.node_b, latency=12.5)
        Edge.objects.create(source=self.node_b, destination=self.node_d, latency=10.9)

        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerD'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data['total_latency'], 23.4, places=1)
        self.assertEqual(response.data['path'], ['ServerA', 'ServerB', 'ServerD'])

    def test_shortest_route_no_path(self):
        """POST /routes/shortest - 404 when no path exists."""
        Edge.objects.create(source=self.node_a, destination=self.node_b, latency=12.5)
        # No edge from B or A to D

        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerD'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_shortest_route_invalid_source(self):
        """POST /routes/shortest - 400 when source doesn't exist."""
        response = self.client.post(
            self.url,
            {
                'source': 'NonExistent',
                'destination': 'ServerB'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shortest_route_invalid_destination(self):
        """POST /routes/shortest - 400 when destination doesn't exist."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'NonExistent'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shortest_route_same_source_destination(self):
        """POST /routes/shortest - 400 when source == destination."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerA'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shortest_route_saves_history(self):
        """POST /routes/shortest - Route is saved to history."""
        Edge.objects.create(source=self.node_a, destination=self.node_b, latency=12.5)
        Edge.objects.create(source=self.node_b, destination=self.node_d, latency=10.9)

        self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerD'
            },
            format='json'
        )

        history = RouteHistory.objects.filter(source=self.node_a, destination=self.node_d)
        self.assertEqual(history.count(), 1)
        self.assertAlmostEqual(history.first().total_latency, 23.4, places=1)
