from email.policy import default
from enum import unique

from django.db import models

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Driver(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Race(models.Model):
    name = models.CharField(max_length=100)
    season = models.IntegerField()

    class Meta:
        unique_together = ('season', 'name')

    def __str__(self):
        return f"{self.name} {self.season}"

class PaddockImporter(models.Model):
    run = models.BooleanField(default=False)

    def __str__(self):
        return "Import Paddock Data"