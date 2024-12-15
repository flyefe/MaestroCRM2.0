from django.urls import path
from . import views, views_service, views_traffic_source



urlpatterns = [
    path('update-settings/', views.update_settings, name='update_settings'),

    # Services
    path('service/', views_service.service_list, name='service_list'),
    path('edit-service/<int:service_id>/', views_service.edit_service, name='edit_service'),
    path('delete-service/<int:service_id>/', views_service.delete_service, name='delete_service'),

    #Traffic Source
    path('traffic-source-list/', views_traffic_source.traffic_source_list, name='traffic_source_list'),
    path('edit-traffic-source/<int:traffic_source_id>/', views_traffic_source.delete_traffic_source, name='edit_traffic_source'),
    path('delete-traffic-source/<int:traffic_source_id>/', views_traffic_source.delete_traffic_source, name='delete_traffic_source'),



    
    


]