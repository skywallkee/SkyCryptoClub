from django.db import models
from django.utils import timezone


class Update(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    date = models.DateTimeField(default=timezone.now)
    released = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ". " + self.title


class Feature(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    featureType = models.CharField(max_length=25, null=True, blank=True)
    update = models.ForeignKey(Update, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title