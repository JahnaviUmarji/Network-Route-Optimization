from rest_framework import serializers

from .models import Edge, Node, RouteHistory


class NodeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Node
		fields = ['id', 'name', 'created_at', 'updated_at']
		extra_kwargs = {
			'name': {'validators': []}  # Remove unique constraint from serializer
		}

	def validate_name(self, value):
		if not value or not value.strip():
			raise serializers.ValidationError('Node name must not be empty.')
		return value.strip()


class EdgeSerializer(serializers.ModelSerializer):
	source = serializers.SlugRelatedField(slug_field='name', queryset=Node.objects.all())
	destination = serializers.SlugRelatedField(slug_field='name', queryset=Node.objects.all())

	class Meta:
		model = Edge
		fields = ['id', 'source', 'destination', 'latency', 'created_at', 'updated_at']
		extra_kwargs = {
			'source': {'validators': []},
			'destination': {'validators': []},
		}
		validators = []  # Disable all model-level validators

	def validate_latency(self, value):
		if value is None or value <= 0.0:
			raise serializers.ValidationError('Latency must be a positive number.')
		return value

	def validate(self, data):
		source = data.get('source')
		destination = data.get('destination')

		if source == destination:
			raise serializers.ValidationError('Source and destination must be different.')

		# DO NOT validate unique_together here — let get_or_create handle it
		return data

	def create(self, validated_data):
		"""Override to use get_or_create for idempotency."""
		source = validated_data['source']
		destination = validated_data['destination']
		latency = validated_data['latency']

		edge, created = Edge.objects.get_or_create(
			source=source,
			destination=destination,
			defaults={'latency': latency}
		)

		# Update latency if different
		if not created and edge.latency != latency:
			edge.latency = latency
			edge.save()

		return edge

	def to_representation(self, instance):
		"""Override to return node names instead of objects."""
		ret = super().to_representation(instance)
		ret['source'] = instance.source.name
		ret['destination'] = instance.destination.name
		return ret


class RouteHistorySerializer(serializers.ModelSerializer):
	source = serializers.CharField(source='source.name', read_only=True)
	destination = serializers.CharField(source='destination.name', read_only=True)

	class Meta:
		model = RouteHistory
		fields = ['id', 'source', 'destination', 'total_latency', 'path', 'created_at']


class RouteQuerySerializer(serializers.Serializer):
	source = serializers.CharField(max_length=255)
	destination = serializers.CharField(max_length=255)

	def validate_source(self, value):
		if not value.strip():
			raise serializers.ValidationError('Source must not be empty.')
		return value.strip()

	def validate_destination(self, value):
		if not value.strip():
			raise serializers.ValidationError('Destination must not be empty.')
		return value.strip()

	def validate(self, attrs):
		if attrs.get('source') == attrs.get('destination'):
			raise serializers.ValidationError('Source and destination must differ.')
		return attrs
