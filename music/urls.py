from django.urls import path
from . import views


app_name = 'music'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login_user'),
    path('<str:username>/create_album/', views.create_album, name='create_album'),
    path('<str:username>/<int:album_id>/', views.detail, name='detail'),
    path('<str:username>/<int:album_id>/create_song/', views.create_song, name='create_song'),
    path('<str:username>/songs/<str:filter_by>/', views.songs, name='songs'),
]
