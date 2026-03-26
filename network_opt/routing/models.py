from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Node(TimeStampedModel):
	name = models.CharField(max_length=255, unique=True)

	class Meta:
		verbose_name_plural = 'Nodes'

	def __str__(self):
		return self.name


class Edge(TimeStampedModel):
	source = models.ForeignKey(Node, related_name='outgoing_edges', on_delete=models.CASCADE)
	destination = models.ForeignKey(Node, related_name='incoming_edges', on_delete=models.CASCADE)
	latency = models.FloatField()

	class Meta:
		unique_together = ('source', 'destination')
		verbose_name_plural = 'Edges'


	def __str__(self):
		return f"{self.source} -> {self.destination} ({self.latency})"


class RouteHistory(TimeStampedModel):
	source = models.ForeignKey(Node, related_name='route_histories_from', on_delete=models.CASCADE)
	destination = models.ForeignKey(Node, related_name='route_histories_to', on_delete=models.CASCADE)
	total_latency = models.FloatField()
	path = models.JSONField()

	class Meta:
		verbose_name_plural = 'Route Histories'

	def __str__(self):
		return f"{self.source} -> {self.destination} ({self.total_latency}) at {self.created_at.isoformat()}"



