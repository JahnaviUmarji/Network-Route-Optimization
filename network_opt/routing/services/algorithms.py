import heapq
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class PathFindingAlgorithm(ABC):
    """Abstract base class for pathfinding algorithms (Strategy pattern)."""

    @abstractmethod
    def find_shortest_path(
        self, adjacency: Dict[str, List[Tuple[str, float]]], source: str, destination: str
    ) -> Optional[Tuple[float, List[str]]]:
        """
        Find shortest path between source and destination.

        Args:
            adjacency: Adjacency list {node: [(neighbor, latency), ...]}.
            source: Source node name.
            destination: Destination node name.

        Returns:
            Tuple of (total_latency, path) or None if no path exists.
        """
        pass


class DijkstraAlgorithm(PathFindingAlgorithm):
    """Dijkstra's shortest path algorithm."""

    def find_shortest_path(
        self, adjacency: Dict[str, List[Tuple[str, float]]], source: str, destination: str
    ) -> Optional[Tuple[float, List[str]]]:
        """
        Find shortest path using Dijkstra's algorithm.

        Args:
            adjacency: Adjacency list {node: [(neighbor, latency), ...]}.
            source: Source node name.
            destination: Destination node name.

        Returns:
            Tuple of (total_latency, path) or None if no path exists.
        """
        if source not in adjacency or destination not in adjacency:
            return None

        distances = {node: float('inf') for node in adjacency}
        distances[source] = 0.0
        predecessors = {node: None for node in adjacency}
        heap = [(0.0, source)]
        visited = set()

        while heap:
            current_distance, current_node = heapq.heappop(heap)

            if current_node in visited:
                continue

            visited.add(current_node)

            if current_node == destination:
                path = []
                node = destination
                while node is not None:
                    path.append(node)
                    node = predecessors[node]
                path.reverse()
                return (current_distance, path)

            if current_distance > distances[current_node]:
                continue

            for neighbor, latency in adjacency[current_node]:
                new_distance = current_distance + latency
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(heap, (new_distance, neighbor))

        return None
