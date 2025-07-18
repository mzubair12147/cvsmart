from django import forms
from .models import ResumeUpload
import os

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = ResumeUpload
        fields = ['file', 'job_description']

    def clean_file(self):
        file = self.cleaned_data.get('file')

        # 1. Check extension
        ext = os.path.splitext(file.name)[1].lower()
        if ext != '.pdf':
            raise forms.ValidationError("Only PDF files are allowed.")

        # 2. Check size (limit: 5MB = 5 * 1024 * 1024 bytes)
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError("File size must not exceed 5MB.")

        return file