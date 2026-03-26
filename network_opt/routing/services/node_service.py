from django.core.exceptions import ValidationError
from django.db import IntegrityError

from routing.models import Node


class NodeService:
    """Service for managing Node operations."""

    @staticmethod
    def create_node(name: str) -> tuple:
        """
        Create or get a node (idempotent).

        Args:
            name: Unique node identifier.

        Returns:
            Tuple of (Node instance, created: bool) where created=True if newly created.

        Raises:
            ValidationError: If name is empty.
        """
        if not name or not name.strip():
            raise ValidationError("Node name must not be empty.")

        node, created = Node.objects.get_or_create(name=name.strip())
        return node, created

    @staticmethod
    def get_node_by_id(node_id: int) -> Node:
        """
        Retrieve a node by ID.

        Args:
            node_id: Node primary key.

        Returns:
            Node instance.

        Raises:
            Node.DoesNotExist: If node not found.
        """
        return Node.objects.get(id=node_id)

    @staticmethod
    def get_node_by_name(name: str) -> Node:
        """
        Retrieve a node by name.

        Args:
            name: Node name.

        Returns:
            Node instance.

        Raises:
            Node.DoesNotExist: If node not found.
        """
        return Node.objects.get(name=name.strip())

    @staticmethod
    def list_nodes():
        """List all nodes."""
        return Node.objects.all()

    @staticmethod
    def delete_node(node_id: int) -> None:
        """
        Delete a node by ID.

        Args:
            node_id: Node primary key.

        Raises:
            Node.DoesNotExist: If node not found.
        """
        node = Node.objects.get(id=node_id)
        node.delete()
