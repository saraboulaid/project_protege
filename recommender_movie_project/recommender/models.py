# Create your models here.
from django.db import models

# Create your models here.
from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    favorite_genres = models.CharField(max_length=255)  # Genres préférés séparés par des virgules
    favorite_authors = models.CharField(max_length=255, blank=True)  # Auteurs préférés

    def __str__(self):
        return self.username

