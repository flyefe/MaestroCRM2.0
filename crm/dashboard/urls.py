from django.urls import path
# from . import views
from . import views

#Urls patterns
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('staff/<int:staff_id>/contacts/', views.dashboard, name='staff_contacts'),
]