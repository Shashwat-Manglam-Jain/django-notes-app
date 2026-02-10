from django.urls import include, path

from .views import NoteView


urlpatterns = [
    path("", include("accounts.urls")),
    path("notes/", NoteView.as_view(), name="notes"),
    path("notes/<int:id>/", NoteView.as_view(), name="note-detail"),
]
