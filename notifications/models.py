import uuid
from django.db import models
from utils.models import BaseModel

from users.models import CustomUser

# Create your models here.
class Notification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    delivered =  models.BooleanField(default=False)
    
    def __str__(self):
        return self.message