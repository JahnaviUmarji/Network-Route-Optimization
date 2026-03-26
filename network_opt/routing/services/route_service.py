from django.core.exceptions import ValidationError

from routing.models import Node, RouteHistory
from routing.services.algorithms import DijkstraAlgorithm, PathFindingAlgorithm
from routing.services.edge_service import EdgeService


class RouteService:
    """Service for computing shortest routes and managing route history."""

    def __init__(self, algorithm: PathFindingAlgorithm = None):
        """
        Initialize with a pathfinding algorithm.

        Args:
            algorithm: PathFindingAlgorithm instance. Defaults to Dijkstra.
        """
        self.algorithm = algorithm or DijkstraAlgorithm()

    def find_shortest_route(
        self, source_name: str, destination_name: str
    ) -> tuple:
        """
        Find shortest route between two nodes and save to history.

        Args:
            source_name: Source node name.
            destination_name: Destination node name.

        Returns:
            Tuple of (total_latency, path) where path is list of node names.

        Raises:
            ValidationError: If nodes invalid or don't exist.
            ValueError: If no path exists.
        """
        if not source_name or not source_name.strip():
            raise ValidationError("Source node name must not be empty.")

        if not destination_name or not destination_name.strip():
            raise ValidationError("Destination node name must not be empty.")

        source_name = source_name.strip()
        destination_name = destination_name.strip()

        if source_name == destination_name:
            raise ValidationError("Source and destination must be different.")

        try:
            source_node = Node.objects.get(name=source_name)
        except Node.DoesNotExist as e:
            raise ValidationError(f"Source node '{source_name}' does not exist.") from e

        try:
            destination_node = Node.objects.get(name=destination_name)
        except Node.DoesNotExist as e:
            raise ValidationError(
                f"Destination node '{destination_name}' does not exist."
            ) from e

        adjacency = EdgeService.get_adjacency_list()
        result = self.algorithm.find_shortest_path(adjacency, source_name, destination_name)

        if result is None:
            raise ValueError(f"No path exists between {source_name} and {destination_name}")

        total_latency, path = result

        route_history = RouteHistory.objects.create(
            source=source_node, destination=destination_node, total_latency=total_latency, path=path
        )

        return (total_latency, path)

    @staticmethod
    def get_route_history(source=None, destination=None, limit=None, date_from=None, date_to=None):
        """
        Retrieve route history with optional filters.

        Args:
            source: Filter by source node name (optional).
            destination: Filter by destination node name (optional).
            limit: Max number of results (optional).
            date_from: Filter by created_at >= date_from (optional).
            date_to: Filter by created_at <= date_to (optional).

        Returns:
            QuerySet of RouteHistory records.
        """
        queryset = RouteHistory.objects.all()

        if source:
            queryset = queryset.filter(source__name=source.strip())

        if destination:
            queryset = queryset.filter(destination__name=destination.strip())

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        queryset = queryset.order_by('-created_at')

        if limit:
            queryset = queryset[:limit]

        return queryset
