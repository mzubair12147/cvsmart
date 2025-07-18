import os
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import ResumeUpload
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ResumeUploadForm
from .utils import extract_and_save_resume_text
import json

@login_required
def upload_resume_view(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            file_path = resume.file.path  # ✅ path to file on disk
            extract_and_save_resume_text(resume.id, file_path)

            messages.success(request, "Resume uploaded and analyzed successfully.")
            return redirect('resume_analysis_result', resume_id = resume.id)
        else:
            messages.error(request, "Invalid upload. Please try again.")
    else:
        form = ResumeUploadForm()

    return render(request, 'analyzer/upload_resume.html', {'form': form})


@login_required 
def upload_success(request):
    return render(request,"analyzer/upload_success.html",context={"file_name": "No File Name"} )

@login_required
def resume_analysis_result(request, resume_id):
    try:
        resume = get_object_or_404(ResumeUpload, id = resume_id, user=request.user)
        result = json.loads(resume.analysis_result or "{}") 
    except Exception as e:
        result = {"error" : "Results are not a valid JSON Format!"}

    return render(request, "analyzer/analysis_result.html", context={
        "resume" : resume,
        "result": result
    } )



@login_required
def history_view(request):
    resumes=  ResumeUpload.objects.filter(user=request.user).order_by("uploaded_at")
    return render(request,"analyzer/history.html", context={"resumes": resumes})
