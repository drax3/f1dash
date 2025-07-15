from random import choice

from django.db import models
from paddock.models import Driver, Race, Team

# Create your models here.
class DriverComparison(models.Model):
    COMPARISON_TYPES = [
        ('scatter_laps', 'Race Laps'),
        ('throttle_brake', 'Throttle vs Brake'),
        ('speed_distribution', 'Speed Bins')
    ]

    season = models.IntegerField()
    race = models.ForeignKey(Race, on_delete=models.CASCADE)

    driver1 = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='telemetry_driver1')
    driver2 = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='telemetry_driver2')

    comparison_type = models.CharField(max_length=50, choices=COMPARISON_TYPES)
    plot_base64 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('season', 'race', 'driver1', 'driver2', 'comparison_type')

    def __str__(self):
        return f"{self.season} {self.race.name} | {self.driver1.code} vs {self.driver2.code} ({self.comparison_type})"