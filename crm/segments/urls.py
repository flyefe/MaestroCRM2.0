from django.urls import path
from . import views

app_name = 'segments'

urlpatterns = [
    path('', views.segment_list, name='list'),
    path('contacts/<int:pk>/', views.segment_contacts, name='contacts'),
    path('edit/<int:pk>/', views.edit_segment, name='edit'),
    path('delete/<int:pk>/', views.delete_segment, name='delete'),
    path('bulk-action/', views.bulk_action, name='bulk_action'),
    path('add/', views.add_segment, name='add'),
]
