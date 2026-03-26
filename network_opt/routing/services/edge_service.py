from django.core.exceptions import ValidationError
from django.db import IntegrityError

from routing.models import Edge, Node


class EdgeService:
    """Service for managing Edge operations and adjacency."""

    @staticmethod
    def create_edge(source_name: str, destination_name: str, latency: float) -> tuple:
        """
        Create or get an edge (idempotent).

        Args:
            source_name: Source node name.
            destination_name: Destination node name.
            latency: Latency value (must be positive).

        Returns:
            Tuple of (Edge instance, created: bool) where created=True if newly created.

        Raises:
            ValidationError: On invalid input or business rule violation.
        """
        if latency is None or latency <= 0.0:
            raise ValidationError("Latency must be a positive number.")

        if not source_name or not source_name.strip():
            raise ValidationError("Source node name must not be empty.")

        if not destination_name or not destination_name.strip():
            raise ValidationError("Destination node name must not be empty.")

        source_name = source_name.strip()
        destination_name = destination_name.strip()

        if source_name == destination_name:
            raise ValidationError("Source and destination must be different.")

        try:
            source = Node.objects.get(name=source_name)
        except Node.DoesNotExist as e:
            raise ValidationError(f"Source node '{source_name}' does not exist.") from e

        try:
            destination = Node.objects.get(name=destination_name)
        except Node.DoesNotExist as e:
            raise ValidationError(f"Destination node '{destination_name}' does not exist.") from e

        edge, created = Edge.objects.get_or_create(
            source=source, destination=destination, defaults={'latency': latency}
        )

        # If edge already exists, validate latency matches (or allow update)
        if not created and edge.latency != latency:
            edge.latency = latency
            edge.save()

        return edge, created

    @staticmethod
    def get_edge_by_id(edge_id: int) -> Edge:
        """
        Retrieve an edge by ID.

        Args:
            edge_id: Edge primary key.

        Returns:
            Edge instance.

        Raises:
            Edge.DoesNotExist: If edge not found.
        """
        return Edge.objects.get(id=edge_id)

    @staticmethod
    def list_edges():
        """List all edges."""
        return Edge.objects.all()

    @staticmethod
    def delete_edge(edge_id: int) -> None:
        """
        Delete an edge by ID.

        Args:
            edge_id: Edge primary key.

        Raises:
            Edge.DoesNotExist: If edge not found.
        """
        edge = Edge.objects.get(id=edge_id)
        edge.delete()

    @staticmethod
    def get_adjacency_list() -> dict:
        """
        Build an in-memory adjacency list for pathfinding.

        Returns:
            Dict mapping node names to list of (neighbor_name, latency) tuples.
        """
        adjacency = {}
        for node in Node.objects.all():
            adjacency[node.name] = []

        for edge in Edge.objects.all():
            adjacency[edge.source.name].append((edge.destination.name, edge.latency))

        return adjacency
