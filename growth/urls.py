from django.urls import path

from growth import views

app_name = "growth"

urlpatterns = [
    path("join/<str:code>/", views.join_referral, name="join"),
    path("email-capture/", views.email_capture, name="email-capture"),
    path("stats/", views.stats_partial, name="stats"),
    path("launch/", views.launch_page, name="launch"),
    path("student/", views.student_page, name="student"),
]
