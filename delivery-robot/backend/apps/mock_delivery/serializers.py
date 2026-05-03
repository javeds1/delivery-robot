from rest_framework import serializers


class ExtIdPointSerializer(serializers.Serializer):
    extId = serializers.CharField(max_length=255)


class LatLonPointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)


class CreateInputSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    extId = serializers.CharField(max_length=255, required=False, allow_blank=True)
    robot = serializers.CharField(max_length=255, required=False, allow_blank=True)
    clientName = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.CharField(max_length=255, required=False, allow_blank=True)
    webhook = serializers.CharField(max_length=1024, required=False, allow_blank=True)
    scheduledPickUp = serializers.DateTimeField(required=False)
    src = serializers.JSONField(required=False)
    dst = serializers.JSONField(required=True)

    def validate(self, attrs):
        attrs["src"] = self._validate_point(attrs.get("src"), field_name="src", required=False)
        attrs["dst"] = self._validate_point(attrs.get("dst"), field_name="dst", required=True)
        return attrs

    def _validate_point(self, value, field_name: str, required: bool):
        if value is None:
            if required:
                raise serializers.ValidationError({field_name: "This field is required."})
            return None

        if "extId" in value:
            serializer = ExtIdPointSerializer(data=value)
            serializer.is_valid(raise_exception=True)
            return serializer.validated_data

        serializer = LatLonPointSerializer(data=value)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class OrderRequestPointSerializer(serializers.Serializer):
    address = serializers.CharField(allow_null=True)


class OrderRequestSerializer(serializers.Serializer):
    src = OrderRequestPointSerializer()
    dst = OrderRequestPointSerializer()
    clientName = serializers.CharField(required=False, allow_blank=True)


class ETASerializer(serializers.Serializer):
    pickUp = serializers.DateTimeField()
    dropOff = serializers.DateTimeField()
    return_eta = serializers.DateTimeField(source="return")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["return"] = data.pop("return_eta")
        return data


class PositionSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    yaw = serializers.FloatField()


class RobotStateSerializer(serializers.Serializer):
    name = serializers.CharField()
    position = PositionSerializer()
    route = LatLonPointSerializer(many=True, allow_null=True)
    deliveringOtherOrders = serializers.BooleanField()


class OrderPointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    address = serializers.CharField(required=False, allow_blank=True)
    extId = serializers.CharField(required=False, allow_blank=True)


class OrderStateSerializer(serializers.Serializer):
    id = serializers.CharField()
    extId = serializers.CharField(allow_null=True)
    src = OrderPointSerializer()
    dst = OrderPointSerializer()
    scheduledPickUp = serializers.DateTimeField()
    request = OrderRequestSerializer()
    createdAt = serializers.DateTimeField()
    status = serializers.CharField()
    ready = serializers.BooleanField()
    eta = ETASerializer()
    robots = RobotStateSerializer(many=True, allow_null=True)


class OrdersResponseSerializer(serializers.Serializer):
    orders = OrderStateSerializer(many=True, allow_null=True)


class RobotsResponseSerializer(serializers.Serializer):
    robots = RobotStateSerializer(many=True, allow_null=True)


class ExternalFeaturesSerializer(serializers.Serializer):
    adminOperations = serializers.BooleanField()
    basicOperations = serializers.BooleanField()
    cancelOrder = serializers.BooleanField()
    createOrder = serializers.BooleanField()
    dropOffOrder = serializers.BooleanField()
    loadOrder = serializers.BooleanField()
    manageOrder = serializers.BooleanField()
    returnToPickUp = serializers.BooleanField()
    viewOrder = serializers.BooleanField()
    viewRobots = serializers.BooleanField()


class UIConfigSerializer(serializers.Serializer):
    dispatchRadius = serializers.FloatField(allow_null=True)
    countryCode = serializers.CharField()
    omitPhone = serializers.BooleanField()
    newOrderSound = serializers.BooleanField()
    predefinedOrders = serializers.ListField(child=serializers.DictField(), allow_null=True, required=False)


class UIUserSerializer(serializers.Serializer):
    firstName = serializers.CharField(allow_null=True)
    lastName = serializers.CharField(allow_null=True)
    login = serializers.CharField()
    email = serializers.CharField()
    roles = serializers.ListField(child=serializers.CharField(), allow_null=True)
    partnerId = serializers.CharField()
    features = ExternalFeaturesSerializer()
    config = UIConfigSerializer(required=False)
