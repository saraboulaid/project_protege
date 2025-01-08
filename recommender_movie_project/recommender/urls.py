from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
     path('sparql/', views.sparql_query, name='sparql_query'),
]
