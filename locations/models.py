import uuid
from django.db import models
from utils.models import BaseModel

from users.models import PeerA, PeerB

STATUS = (
    ("IN-PROGRESS", "IN-PROGRESS"),
    ("WAITING", "WAITING"),
    ("CANCELLED", "CANCELLED"),
    ("COMPLETED", "COMPLETED"),
)

class ShareLocationRequestModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peer_a = models.ForeignKey(PeerA, on_delete=models.CASCADE)
    peer_b = models.ForeignKey(PeerB, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=50)

    def __str__(self):
        return f'{self.id}'

