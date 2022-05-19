from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('logout/', views.logout_user, name='logout'),
]