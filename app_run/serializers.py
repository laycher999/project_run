from geopy.distance import geodesic
from rest_framework import serializers

from .models import Run, User, AthleteInfo, Challenges, Positions, CollectibleItem, Subscribe


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



class AthleteSerializerDetailed(UserSerializerDetailed):
    coach = serializers.SerializerMethodField()
    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializerDetailed.Meta.fields + ['coach']

    def get_coach(self, obj):
        sub = Subscribe.objects.filter(athlete_id=obj.id).first()
        coach_id = sub.coach_id if sub else None
        return coach_id

class CoachSerializerDetailed(UserSerializerDetailed):
    athletes = serializers.SerializerMethodField()
    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['athletes']

    def get_athletes(self, obj):
        athletes = Subscribe.objects.filter(coach_id=obj.id).values_list('athlete_id', flat=True)
        print(athletes)
        return athletes


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
        fields = ['run', 'latitude', 'longitude', 'date_time', 'speed', 'distance']

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
        fields = ['id', 'athlete', 'athlete_data', 'created_at', 'comment', 'status', 'distance', 'run_time_seconds', 'speed']


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

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['athlete_id', 'coach_id']





