from django.db import models
from utils.models import BaseModel

from users.models import CustomUser

# Create your models here.
class Notification(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    
    def __str__(self):
        return self.message