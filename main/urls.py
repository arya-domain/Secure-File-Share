from django.urls import path
from . import views
from django.urls import include

# url config
urlpatterns = [
    path(route="", view=views.upload_file, name="home"),
    path(route="signup/", view=views.register, name="signup"),
    path(route="accounts/", view=include("django.contrib.auth.urls")),
    path(route="upload/", view=views.upload_file, name="upload"),
    path(route="list/", view=views.view_uploaded_files, name="list"),
    path(route="download/", view=views.download_file, name="download_file"),
    path(route='generate-key/', view=views.generate_key_view, name='generate_key'),
    path('get-users/', view=views.get_users, name='get_users'),
    path('generate-encrypted-text/', views.generate_encrypted_text, name='generate_encrypted_text'),
    path('download-history/', views.download_history, name='download_history'),
]
