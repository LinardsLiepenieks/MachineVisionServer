from django.db import models

class ObjectKeyword(models.Model):
    keyword = models.CharField(max_length=100, unique=True)
    identifier = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.keyword} ({self.identifier})"

class ActionVerb(models.Model):
    verb = models.CharField(max_length=100, unique=True)
    identifier = models.CharField(max_length=100, unique=True)
    related_words = models.TextField(blank=True)  # Store as comma-separated values

    def set_related_words(self, words):
        self.related_words = ','.join(words)

    def get_related_words(self):
        return self.related_words.split(',') if self.related_words else []

    def __str__(self):
        return f"{self.verb} ({self.identifier})"
