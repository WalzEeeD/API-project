from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)  # User's unique username
    email = models.EmailField(unique=True) 
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created


    def __str__(self):
        return self.username

class Post(models.Model):
    content = models.TextField()  # The text content of the post
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the post was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the post was last updated


    def __str__(self):
        return self.content[:50]

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

class Task(models.Model):
    TASK_TYPES = [
        ('regular', 'Regular'),
        ('priority', 'Priority'),
        ('recurring', 'Recurring'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
