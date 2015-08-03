from rest_framework import fields, serializers
from .models import UserVideoMetric


class UserVideoMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVideoMetric
        validators = []


class MonthMetricsSerializer(serializers.Serializer):
    dates = fields.ListField(
        child=fields.CharField(min_length=3, max_length=5)
    )
    video_seconds_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    audio_seconds_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    total_seconds_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    video_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    audio_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    total_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0)
    )
    archive_video_seconds_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_audio_seconds_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_total_seconds_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_video_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_audio_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
    archive_total_plays_list = fields.ListField(
        child=fields.IntegerField(min_value=0),
        required=False
    )
