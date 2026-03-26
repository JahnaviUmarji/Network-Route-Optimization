from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from routing.models import Node


class NodeAPITestCase(TestCase):
    """Test Node CRUD endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/nodes/'

    def test_create_node_success(self):
        """POST /nodes - Create node successfully."""
        response = self.client.post(self.url, {'name': 'ServerA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'ServerA')
        self.assertIn('id', response.data)

    def test_create_node_missing_name(self):
        """POST /nodes - 400 when name missing."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_node_empty_name(self):
        """POST /nodes - 400 when name is empty/whitespace."""
        response = self.client.post(self.url, {'name': '   '}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_node_duplicate(self):
        """POST /nodes - 200 when name already exists (idempotent)."""
        self.client.post(self.url, {'name': 'ServerA'}, format='json')
        response = self.client.post(self.url, {'name': 'ServerA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_nodes(self):
        """GET /nodes - List all nodes."""
        Node.objects.create(name='ServerA')
        Node.objects.create(name='ServerB')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_node(self):
        """DELETE /nodes/{id} - Delete node."""
        node = Node.objects.create(name='ServerA')
        response = self.client.delete(f'{self.url}{node.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Node.objects.filter(id=node.id).exists())
