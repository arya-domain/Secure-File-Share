from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Download(models.Model):
    user_id = models.CharField(max_length=100)
    download_time = models.DateTimeField(default=datetime.now)
    filename = models.CharField(max_length=255)

    @classmethod
    def create(cls, user_id, file_path):
        filename = file_path.split("\\")[0] 
        return cls(user_id=user_id, filename=filename)

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    encryption_key = models.CharField(max_length=255) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_path
