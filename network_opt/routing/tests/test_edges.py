from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from routing.models import Node, Edge


class EdgeAPITestCase(TestCase):
    """Test Edge CRUD endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/edges/'
        self.node_a = Node.objects.create(name='ServerA')
        self.node_b = Node.objects.create(name='ServerB')
        self.node_c = Node.objects.create(name='ServerC')

    def test_create_edge_success(self):
        """POST /edges - Create edge successfully."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerB',
                'latency': 12.5
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['latency'], 12.5)
        self.assertIn('id', response.data)

    def test_create_edge_invalid_latency_zero(self):
        """POST /edges - 400 when latency <= 0."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerB',
                'latency': 0
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_invalid_latency_negative(self):
        """POST /edges - 400 when latency negative."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerB',
                'latency': -5.0
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_missing_source(self):
        """POST /edges - 400 when source missing."""
        response = self.client.post(
            self.url,
            {
                'destination': 'ServerB',
                'latency': 12.5
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_missing_destination(self):
        """POST /edges - 400 when destination missing."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'latency': 12.5
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_source_not_found(self):
        """POST /edges - 400 when source node doesn't exist."""
        response = self.client.post(
            self.url,
            {
                'source': 'NonExistent',
                'destination': 'ServerB',
                'latency': 12.5
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_destination_not_found(self):
        """POST /edges - 400 when destination node doesn't exist."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'NonExistent',
                'latency': 12.5
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_duplicate(self):
        """POST /edges - 200 when edge already exists (idempotent, updates latency)."""
        self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerB',
                'latency': 12.5
            },
            format='json'
        )
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerB',
                'latency': 15.0
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['latency'], 15.0)

    def test_create_edge_same_source_destination(self):
        """POST /edges - 400 when source == destination."""
        response = self.client.post(
            self.url,
            {
                'source': 'ServerA',
                'destination': 'ServerA',
                'latency': 12.5
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_edges(self):
        """GET /edges - List all edges."""
        Edge.objects.create(source=self.node_a, destination=self.node_b, latency=12.5)
        Edge.objects.create(source=self.node_b, destination=self.node_c, latency=10.1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_edge(self):
        """DELETE /edges/{id} - Delete edge."""
        edge = Edge.objects.create(source=self.node_a, destination=self.node_b, latency=12.5)
        response = self.client.delete(f'{self.url}{edge.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Edge.objects.filter(id=edge.id).exists())
