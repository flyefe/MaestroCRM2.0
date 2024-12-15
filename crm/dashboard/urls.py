from django.urls import path
# from . import views
from . import views

#Urls patterns
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]