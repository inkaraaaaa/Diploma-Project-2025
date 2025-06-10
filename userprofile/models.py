from django.db import models
from django.contrib.auth import get_user_model
import os
from django.conf import settings

User = get_user_model()

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    upload = models.FileField(upload_to='documents/')

    def delete(self, *args, **kwargs):
        if self.upload and os.path.isfile(self.upload.path):
            os.remove(self.upload.path)
        super().delete(*args, **kwargs)
