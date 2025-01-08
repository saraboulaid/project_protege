from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('about', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('sparql/', views.sparql_query, name='sparql_query'),
]
