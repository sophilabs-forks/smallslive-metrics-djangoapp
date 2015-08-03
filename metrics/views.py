from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserVideoMetric
from .serializers import MonthMetricsSerializer, UserVideoMetricSerializer


class MetricView(generics.CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserVideoMetric
    serializer_class = UserVideoMetricSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            try:
                now = timezone.now()
                metric = UserVideoMetric.objects.select_for_update().get(
                    media_id=serializer.validated_data.get('media_id'),
                    user_id=serializer.validated_data.get('user_id'),
                    date=now.date()
                )
                if self.passes_validation(now, metric):
                    http_status = status.HTTP_204_NO_CONTENT
                    metric.seconds_played = F('seconds_played') + settings.PING_INTERVAL
                    metric.last_ping = now
                    metric.save()
                else:
                    http_status = status.HTTP_403_FORBIDDEN
            except UserVideoMetric.DoesNotExist:
                self.perform_create(serializer)
                http_status = status.HTTP_201_CREATED
        return Response(status=http_status)

    def passes_validation(self, now, metric):
        allowed_ping_interval = (now >= (metric.last_ping + timedelta(seconds=settings.PING_INTERVAL)))
        less_than_daily_limit = metric.seconds_played <= settings.DAILY_LIMIT_PER_MEDIA
        return allowed_ping_interval and less_than_daily_limit

    def perform_create(self, serializer):
        serializer.save()

metric_view = MetricView.as_view()


class EventCountsView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            month = int(request.query_params.get('month'))
            year = int(request.query_params.get('year'))
            event_id = int(request.query_params.get('event_id'))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        counts = UserVideoMetric.objects.date_counts(month, year, [event_id])
        print counts
        s = MonthMetricsSerializer(data=counts)
        if s.is_valid():
            return Response(data=s.data)
        print s.errors
        return Response(status=status.HTTP_400_BAD_REQUEST)

event_counts = EventCountsView.as_view()


class ArtistCountsView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        print self
        print request.user
        try:
            month = int(request.data.get('month'))
            year = int(request.data.get('year'))
            event_ids = request.data.get('event_ids')
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        counts = UserVideoMetric.objects.date_counts(month, year, event_ids)
        archive_counts = UserVideoMetric.objects.date_counts(month, year)
        for key, val in archive_counts.items():
            new_key = "archive_" + key
            counts[new_key] = val
        s = MonthMetricsSerializer(data=counts)
        if s.is_valid():
            return Response(data=s.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

artist_counts = ArtistCountsView.as_view()
