from django.contrib import admin
from .models import CustomUser, PeerA, PeerB
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(PeerA)
admin.site.register(PeerB)