from django.db import models
from django.utils import timezone


# Create your models here.
class Author(models.Model):
    AuthorName = models.CharField(max_length=25)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.AuthorName


class Story(models.Model):
    CATEGORY_CHOICES = [
        ('pol', 'Politics'),
        ('art', 'Art'),
        ('tech', 'Technology'),
        ('trivia', 'Trivia'),
    ]

    REGION_CHOICES = [
        ('uk', 'UK'),
        ('eu', 'Europe'),
        ('w', 'World'),
    ]

    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    region = models.CharField(max_length=25, choices=REGION_CHOICES)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    details = models.CharField(max_length=128)

    def __str__(self):
        return self.headline
