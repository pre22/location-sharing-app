from django.db import models

# Create your models here.
class Notification(models.Model):
    message = models.CharField(max_length=100)
    
    def __str__(self):
        return self.message