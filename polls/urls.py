from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("vote/", views.vote, name="vote"),
    path("storeVotes/", views.storeVotes, name="storeVotes"),
    path("thankyou/", views.thankyou, name="thankyou"),
    path("grade/", views.grade, name="grade"),
    path("dryRunGrades/", views.dryRunGrades, name="dryRunGrades"),
    path("storeResults/", views.storeResults, name="storeResults"),
    path("gradingcomplete/", views.gradingcomplete, name="gradingcomplete"),
    path("results/", views.results, name="results"),
    path("finale/", views.finale, name="finale"),
    path("error/", views.error, name="error"),
    path("email/", views.email, name="email"),
]