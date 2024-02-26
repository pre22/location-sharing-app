from django.db import models


class BaseModel(models.Model):
    """Adds created_at and modified_at field to a model
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)
