from django.db import models

# Create your models here.
class AnalyzedText(models.Model):
    text = models.TextField()
    keywords = models.TextField(blank=True, null=True)
    entities = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analyzed Text {self.id}"