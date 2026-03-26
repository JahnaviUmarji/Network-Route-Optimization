from django.utils.dateparse import parse_datetime

from routing.models import RouteHistory


class HistoryService:
    """Service for querying and managing route history."""

    @staticmethod
    def get_history(source=None, destination=None, limit=None, date_from=None, date_to=None):
        """
        Retrieve route history with optional filters.

        Args:
            source: Filter by source node name (optional).
            destination: Filter by destination node name (optional).
            limit: Max number of results (optional).
            date_from: Filter by created_at >= date_from (ISO string or datetime, optional).
            date_to: Filter by created_at <= date_to (ISO string or datetime, optional).

        Returns:
            QuerySet of RouteHistory records ordered by created_at descending.
        """
        queryset = RouteHistory.objects.all()

        if source:
            queryset = queryset.filter(source__name=source.strip())

        if destination:
            queryset = queryset.filter(destination__name=destination.strip())

        if date_from:
            if isinstance(date_from, str):
                # Handle URL-encoded + as space (common in query parameters)
                date_from = date_from.replace(' ', '+')
                date_from = parse_datetime(date_from)
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            if isinstance(date_to, str):
                # Handle URL-encoded + as space (common in query parameters)
                date_to = date_to.replace(' ', '+')
                date_to = parse_datetime(date_to)
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)

        queryset = queryset.order_by('-created_at')

        if limit:
            queryset = queryset[:limit]

        return queryset
