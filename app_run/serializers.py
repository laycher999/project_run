from rest_framework import serializers, status
from rest_framework.response import Response

from .models import Run, User, AthleteInfo, Challenges, Positions


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        count = Run.objects.filter(athlete_id=obj.id).filter(status='finished').count()
        return count


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


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)
    class Meta:
        model = Run
        fields = '__all__'


class ChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenges
        fields = ['full_name', 'athlete']


class PositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'

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
