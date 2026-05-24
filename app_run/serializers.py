from rest_framework import serializers

from .models import Run, User, AthleteInfo, Challenges, Positions, CollectibleItem


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'



class UserSerializerDetailed(UserSerializer):
    items = serializers.SerializerMethodField()
    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['items']

    def get_items(self, obj):
        items = CollectibleItem.objects.filter(user=obj)
        serializer = CollectibleItemSerializer(items, many=True)
        return serializer.data



class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    class Meta:
        model = AthleteInfo
        fields = ['goals', 'weight', 'user_id']

    def get_user_id(self, obj):
        return obj.user.id


class PositionsSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')
    class Meta:
        model = Positions
        fields = ['run', 'latitude', 'longitude', 'date_time']

    @staticmethod
    def cords_range(value, cords_range):
        x, y = cords_range
        if value < x or value > y:
            return False
        return True


    def validate_run(self, value):
        if value.status != 'in_progress':
            raise serializers.ValidationError('Run in init or finished status')
        return value


    def validate_latitude(self, value):
        cords_range = (-90, 90)
        if not self.cords_range(value, cords_range):
            raise serializers.ValidationError(f'Values must be in {cords_range} range')
        return value


    def validate_longitude(self, value):
        cords_range = (-180, 180)
        if not self.cords_range(value, cords_range):
            raise serializers.ValidationError(f'Values must be in {cords_range} range')
        return value


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)
    class Meta:
        model = Run
        fields = ['id', 'athlete', 'athlete_data', 'created_at', 'comment', 'status', 'distance', 'run_time_seconds']


class ChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenges
        fields = ['full_name', 'athlete']


class CollectibleItemSerializer(PositionsSerializer):
    class Meta(PositionsSerializer.Meta):
        model = CollectibleItem
        fields = ['name', 'uid', 'latitude', 'longitude', 'value', 'picture']


    def validate_picture(self, value):
        if not value.startswith('https://'):
            raise serializers.ValidationError(f'Incorrect url')
        return value





