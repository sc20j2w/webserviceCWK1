from .views import login, logout, delete, StoryView
from django.urls import path

urlpatterns = [
    path('api/stories', StoryView.as_view(), name='stories'),
    path('api/stories/<int:key>', delete, name='delete_story'),
    path('api/login', login, name='login'),
    path('api/logout', logout, name='logout'),
]
