from django.db import models
from django.contrib.auth.models import User
import time
import os
from slugify import slugify

def resume_upload_path(instance, filename):
    # Get user ID and timestamp
    user_id = instance.user.id
    timestamp = int(time.time())

    # Sanitize filename
    base, ext = os.path.splitext(filename)
    base = slugify(base)

    # Build new filename
    new_filename = f"{user_id}_{timestamp}_{base}{ext}"
    return f"resumes/{new_filename}"

class ResumeUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=resume_upload_path)  # ⬅️ saved in MEDIA_ROOT/resumes/
    uploaded_at = models.DateTimeField(auto_now_add=True)
    job_description = models.TextField()
    extracted_text = models.TextField(blank=True, null=True)
    analysis_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"
    