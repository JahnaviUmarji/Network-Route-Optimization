# Network Route Optimization API

A Django REST Framework API for computing optimal network routes using Dijkstra's shortest path algorithm. Built with SOLID principles and comprehensive test coverage.

## Features

- **Node Management**: Create and list network nodes
- **Edge Management**: Define connections between nodes with latency costs
- **Shortest Path Computation**: Find optimal routes using Dijkstra's algorithm
- **Route History**: Query historical routes with flexible filtering
- **Idempotent API**: Repeated POST requests return existing resources (201 on create, 200 on repeat)
- **Comprehensive Validation**: Input validation at serializer and service layers
- **Strategy Pattern**: Pluggable pathfinding algorithms (extensible for A*, Bellman-Ford, etc.)

## Tech Stack

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: SQLite (persistent)
- **Python**: 3.8+
- **Testing**: Django TestCase with APIClient integration tests

## Project Structure

```
network_opt/
├── network_opt/
│   ├── settings.py          # Django settings, INSTALLED_APPS
│   ├── urls.py              # Root URL router
│   └── wsgi.py
├── routing/
│   ├── models.py            # Domain models (Node, Edge, RouteHistory)
│   ├── serializers.py       # Request/response validation
│   ├── views.py             # HTTP endpoints
│   ├── urls.py              # API URL routing
│   ├── services/
│   │   ├── node_service.py      # Node CRUD operations
│   │   ├── edge_service.py      # Edge CRUD operations
│   │   ├── route_service.py     # Shortest path computation
│   │   ├── history_service.py   # Route history queries
│   │   └── algorithms.py        # Pathfinding algorithms (Dijkstra)
│   └── tests/
│       ├── test_nodes.py        # Node endpoint tests
│       ├── test_edges.py        # Edge endpoint tests
│       ├── test_routes.py       # Route computation tests
│       └── test_history.py      # History filtering tests
├── db.sqlite3               # Persistent database
└── manage.py
```

## API Endpoints

### Nodes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/nodes/` | Create a node (idempotent) |
| GET | `/api/nodes/` | List all nodes |
| DELETE | `/api/nodes/{id}/` | Delete a node |

**Create Node:**
```bash
curl -X POST http://localhost:9000/api/nodes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "ServerA"}'
```

### Edges

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/edges/` | Create an edge with latency (idempotent, updates if exists) |
| GET | `/api/edges/` | List all edges |
| DELETE | `/api/edges/{id}/` | Delete an edge |

**Create Edge:**
```bash
curl -X POST http://localhost:9000/api/edges/ \
  -H "Content-Type: application/json" \
  -d '{"source": "ServerA", "destination": "ServerB", "latency": 12.5}'
```

### Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/routes/shortest/` | Compute shortest path between two nodes |

**Compute Shortest Path:**
```bash
curl -X POST http://localhost:9000/api/routes/shortest/ \
  -H "Content-Type: application/json" \
  -d '{"source": "ServerA", "destination": "ServerD"}'
```

**Response:**
```json
{
  "total_latency": 23.4,
  "path": ["ServerA", "ServerB", "ServerD"]
}
```

### Route History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/routes/history/` | Query route history with filters |

**Query with Filters:**
```bash
# All history
curl http://localhost:9000/api/routes/history/

# Filter by source
curl http://localhost:9000/api/routes/history/?source=ServerA

# Filter by destination
curl http://localhost:9000/api/routes/history/?destination=ServerD

# Filter by date range
curl "http://localhost:9000/api/routes/history/?date_from=2026-03-25T00:00:00%2B00:00&date_to=2026-03-26T00:00:00%2B00:00"

# Limit results
curl "http://localhost:9000/api/routes/history/?limit=10"

# Combine filters
curl "http://localhost:9000/api/routes/history/?source=ServerA&destination=ServerD&limit=5"
```

## Installation & Setup

### 1. Navigate to project directory
```bash
cd "Network-Route-Optimization/network_opt"
```

### 2. Create and activate virtual environment (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install django djangorestframework
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Run the development server
```bash
python manage.py runserver 9000
```

The API will be available at `http://localhost:9000/api/`

## Testing

Run the complete test suite (31 tests):
```bash
python manage.py test routing.tests
```

Run specific test file:
```bash
python manage.py test routing.tests.test_nodes
python manage.py test routing.tests.test_edges
python manage.py test routing.tests.test_routes
python manage.py test routing.tests.test_history
```

Run specific test:
```bash
python manage.py test routing.tests.test_nodes.NodeAPITestCase.test_create_node_success
```

**Test Results**: 31/31 passing ✅

## Design Principles

### SOLID Principles Applied

1. **Single Responsibility**: Each service handles one concern (NodeService manages nodes, EdgeService manages edges, etc.)
2. **Open/Closed**: Algorithm strategy pattern allows adding new pathfinding algorithms without modifying existing code
3. **Liskov Substitution**: `PathFindingAlgorithm` ABC allows swapping implementations (Dijkstra, A*, Bellman-Ford)
4. **Interface Segregation**: Serializers expose only necessary fields; services define clear contracts
5. **Dependency Inversion**: `RouteService` depends on `PathFindingAlgorithm` abstraction, not concrete implementations

### Key Architectural Patterns

- **Strategy Pattern**: `PathFindingAlgorithm` ABC with `DijkstraAlgorithm` implementation
- **Repository Pattern**: Services abstract ORM queries, keeping business logic separate
- **Dependency Injection**: `RouteService` accepts algorithm parameter for flexibility
- **Idempotency**: `get_or_create()` pattern with status code differentiation (201 vs 200)

## Validation Rules

### Nodes
- Name is required and non-empty (after stripping whitespace)
- Name must be unique
- Idempotent: POST same name twice returns 200 OK on second attempt

### Edges
- Source and destination nodes must exist
- Source and destination must be different nodes
- Latency must be positive (> 0)
- Edge is idempotent: POST same edge updates latency if different, returns 200 OK

### Routes
- Source and destination must be valid node names
- Returns 404 if no path exists between nodes
- Saves route to history upon successful computation

### Route History Filters
- `source`: Filter by source node name (string)
- `destination`: Filter by destination node name (string)
- `date_from`: Filter by created_at >= date (ISO 8601 with timezone)
- `date_to`: Filter by created_at <= date (ISO 8601 with timezone)
- `limit`: Maximum number of results (integer)
- Filters are combinable

## Error Handling

All endpoints return appropriate HTTP status codes:

| Status | Scenario |
|--------|----------|
| 200 OK | Successful request or idempotent repeat |
| 201 Created | New resource created |
| 204 No Content | Successful deletion |
| 400 Bad Request | Validation error (invalid data) |
| 404 Not Found | Resource not found or no route exists |

**Error Response Format:**
```json
{
  "error": "Description of what went wrong"
}
```

## Example Workflow

### 1. Create Nodes
```bash
curl -X POST http://localhost:9000/api/nodes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "ServerA"}'
# Returns 201 Created
```

### 2. Create Edges
```bash
curl -X POST http://localhost:9000/api/edges/ \
  -H "Content-Type: application/json" \
  -d '{"source": "ServerA", "destination": "ServerB", "latency": 12.5}'

curl -X POST http://localhost:9000/api/edges/ \
  -H "Content-Type: application/json" \
  -d '{"source": "ServerB", "destination": "ServerC", "latency": 5.2}'
```

### 3. Compute Shortest Path
```bash
curl -X POST http://localhost:9000/api/routes/shortest/ \
  -H "Content-Type: application/json" \
  -d '{"source": "ServerA", "destination": "ServerC"}'
# Returns: {"total_latency": 17.7, "path": ["ServerA", "ServerB", "ServerC"]}
```

### 4. Query History
```bash
curl http://localhost:9000/api/routes/history/
# Returns list of all computed routes with timestamps
```

## Extending the API

### Adding a New Pathfinding Algorithm

1. Create a new algorithm class inheriting from `PathFindingAlgorithm`:

```python
# routing/services/algorithms.py
class AStarAlgorithm(PathFindingAlgorithm):
    """A* pathfinding algorithm implementation."""
    
    def find_shortest_path(self, source_name, destination_name):
        # Implementation here
        return total_cost, path
```

2. Use it in `RouteService`:

```python
algorithm = AStarAlgorithm()
route_service = RouteService(algorithm)
```

### Adding New Filters to Route History

Edit `HistoryService.get_history()` to add new filters:

```python
if some_new_filter:
    queryset = queryset.filter(some_field=some_new_filter)
```

Then update the view to pass the new parameter and update API tests.

## Database Schema

### Node
- `id` (PK): Auto-increment integer
- `name`: Unique CharField (255 chars max)
- `created_at`: Auto-set timestamp
- `updated_at`: Auto-update timestamp

### Edge
- `id` (PK): Auto-increment integer
- `source` (FK): Reference to Node
- `destination` (FK): Reference to Node
- `latency`: FloatField (positive values only)
- `unique_together`: (source, destination)
- `created_at`: Auto-set timestamp
- `updated_at`: Auto-update timestamp

### RouteHistory
- `id` (PK): Auto-increment integer
- `source` (FK): Reference to Node
- `destination` (FK): Reference to Node
- `total_latency`: FloatField
- `path`: JSONField (list of node names)
- `created_at`: Auto-set timestamp
- `updated_at`: Auto-update timestamp

## Performance Considerations

- **Dijkstra's Algorithm**: O(E log V) complexity using heapq
- **Route Queries**: O(1) for node lookups via indexed FK relationships
- **History Filtering**: Uses Django ORM querysets for database-level filtering
- **Pagination**: Can be added via DRF pagination classes if needed

## Future Enhancements

- [ ] Add pagination configuration for large datasets
- [ ] Implement alternative pathfinding algorithms (A*, Bellman-Ford)
- [ ] Add route caching to avoid redundant computations
- [ ] Implement rate limiting and authentication
- [ ] Add WebSocket support for real-time route updates
- [ ] Create admin UI for network topology visualization
- [ ] Add prometheus metrics for monitoring
