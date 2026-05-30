from django.urls import path
from features.api import views

app_name = "api"

urlpatterns = [
    path("v1/jobs/", views.JobSubmitView.as_view(), name="job-submit"),
    path("v1/jobs/<int:job_id>/", views.JobStatusView.as_view(), name="job-status"),
    path("v1/jobs/<int:job_id>/download/", views.JobDownloadView.as_view(), name="job-download"),
    path("v1/tools/", views.ToolListView.as_view(), name="tool-list"),
    path("v1/me/", views.ApiKeyInfoView.as_view(), name="me"),
]
