from django.db import models
from utils.models import BaseModel
# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_peer_one = models.BooleanField(default=False)
    is_peer_two = models.BooleanField(default=False)

    def __str__(self):
        return self.email
    

class PeerA(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
    

class PeerB(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email

