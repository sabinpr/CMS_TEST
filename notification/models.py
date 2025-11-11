from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

