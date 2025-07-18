from django.urls import path
from . import views

urlpatterns = [
    path("upload", views.upload_resume_view, name="upload_resume"),
    path("upload_success/", views.upload_success, name="upload_success"),
    path("result/<int:resume_id>/", views.resume_analysis_result, name="analysis_result"),
    path("history/", views.history_view, name="history")
]