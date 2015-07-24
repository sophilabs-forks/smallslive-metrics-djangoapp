import calendar
from datetime import timedelta
import random

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class MetricsQuerySet(models.QuerySet):
    def total_counts(self):
        return self.aggregate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))


class MetricsManager(models.Manager):
    def get_queryset(self):
        return MetricsQuerySet(self.model, using=self._db)

    def counts_for_recording(self, recording_id):
        return self.get_queryset().filter(recording_id=recording_id).total_counts()

    def counts_for_artist(self, artist_recording_ids):
        return self.get_queryset().filter(recording_id__in=artist_recording_ids).total_counts()

    def total_counts(self):
        return self.get_queryset().total_counts()

    def counts_for_month(self, month, year):
        return self.get_queryset().filter(date__month=month, date__year=year).total_counts()

    def date_counts_for_recording(self, recording_id, month, year):
        values = self.get_queryset().filter(
            recording_id=recording_id, date__month=month, date__year=year).values_list(
            'date', 'play_count', 'seconds_played').order_by('date')
        days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        day_counts = {date.day: count for date, count, seconds in values}
        day_seconds = {date.day: count for date, count, seconds in values}
        counts_list = [day_counts.get(day_number, 0) for day_number in days]
        seconds_list = [day_seconds.get(day_number, 0) for day_number in days]
        return (counts_list, seconds_list)

    def create_random(self):
        today = timezone.now().date()
        params = {}
        params['date'] = today - timedelta(days=random.randrange(1, 90))
        params['recording_id'] = random.randrange(1, 10)
        params['user_id'] = random.randrange(1, 10)
        params['seconds_played'] = random.randrange(10, 600, 10)
        self.create(**params)

    def create_random_for_user(self, user_id):
        today = timezone.now()
        params = {}
        params['user_id'] = user_id
        for day in range(1, 90):
            params['date'] = (today - timedelta(days=day)).date()
            for recording_id in range(1, 5):
                params['recording_id'] = recording_id
                params['seconds_played'] = random.randrange(10, 600, 10)
                params['play_count'] = random.randrange(1, 100, 1)
                print params
                self.create(**params)


class UserVideoMetric(models.Model):
    recording_id = models.IntegerField(blank=False)
    user_id = models.IntegerField(blank=False)
    date = models.DateField(blank=False, default=timezone.now)
    last_ping = models.DateTimeField(auto_now=True)
    seconds_played = models.IntegerField(default=0)
    play_count = models.IntegerField(default=1)  # it gets created on the first play

    objects = MetricsManager()

    class Meta:
        unique_together = ('recording_id', 'user_id', 'date')

    def __str__(self):
        return "V{0} U{1} D{2.year}/{2.month}/{2.day} C{3}".format(
            self.recording_id, self.user_id, self.date, self.seconds_played)
