from django.core.exceptions import ValidationError
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from routing.models import Edge, Node, RouteHistory
from routing.serializers import (
    EdgeSerializer,
    NodeSerializer,
    RouteHistorySerializer,
    RouteQuerySerializer,
)
from routing.services.edge_service import EdgeService
from routing.services.history_service import HistoryService
from routing.services.node_service import NodeService
from routing.services.route_service import RouteService


class NodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Node CRUD operations.
    POST /nodes -> create
    GET /nodes -> list
    DELETE /nodes/{id} -> delete
    """

    queryset = Node.objects.all()
    serializer_class = NodeSerializer

    def create(self, request, *args, **kwargs):
        """POST /nodes - Create or get node (idempotent)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data['name']
        try:
            node, created = NodeService.create_node(name)
            response_serializer = self.get_serializer(node)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(response_serializer.data, status=status_code)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Save node via service."""
        name = serializer.validated_data['name']
        try:
            node, created = NodeService.create_node(name)
            serializer.instance = node
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def list(self, request, *args, **kwargs):
        """GET /nodes - List all nodes."""
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /nodes/{id} - Delete a node."""
        return super().destroy(request, *args, **kwargs)


class EdgeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Edge CRUD operations.
    POST /edges -> create
    GET /edges -> list
    DELETE /edges/{id} -> delete
    """

    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer

    def create(self, request, *args, **kwargs):
        """POST /edges - Create or get edge (idempotent)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source = serializer.validated_data['source'].name
        destination = serializer.validated_data['destination'].name
        latency = serializer.validated_data['latency']

        try:
            edge, created = EdgeService.create_edge(source, destination, latency)
            response_serializer = self.get_serializer(edge)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(response_serializer.data, status=status_code)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Save edge via service."""
        source_name = serializer.validated_data['source'].name
        destination_name = serializer.validated_data['destination'].name
        latency = serializer.validated_data['latency']
        edge, created = EdgeService.create_edge(source_name, destination_name, latency)
        serializer.instance = edge
        serializer.created = created

    def list(self, request, *args, **kwargs):
        """GET /edges - List all edges."""
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /edges/{id} - Delete an edge."""
        return super().destroy(request, *args, **kwargs)


class RouteView(APIView):
    """
    API View for computing shortest route.
    POST /routes/shortest -> compute path, return 200 (found) or 404 (no path).
    """

    def post(self, request):
        """POST /routes/shortest - Compute shortest path."""
        serializer = RouteQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source = serializer.validated_data['source']
        destination = serializer.validated_data['destination']

        try:
            route_service = RouteService()
            total_latency, path = route_service.find_shortest_route(source, destination)

            return Response(
                {'total_latency': total_latency, 'path': path},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )


class RouteHistoryView(APIView):
    """
    API View for querying route history.
    GET /routes/history?source=X&destination=Y&limit=N&date_from=ISO&date_to=ISO
    """

    def get(self, request):
        """GET /routes/history - Retrieve route history with optional filters."""
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')
        limit = request.query_params.get('limit')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if limit:
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'limit must be an integer'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            queryset = HistoryService.get_history(
                source=source,
                destination=destination,
                limit=limit,
                date_from=date_from,
                date_to=date_to,
            )
            serializer = RouteHistorySerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
