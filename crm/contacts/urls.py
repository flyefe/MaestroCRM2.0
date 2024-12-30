from django.urls import path
# from . import views
from . import views, views_status, views_tags, views_import

#Urls patterns
urlpatterns = [
    path('update-log/<int:log_id>/delete', views.delete_log, name='delete_log'),
    path('update-log/<int:log_id>/', views.update_log, name='update_log'),

    path('contacts-by-service/<int:service_id>/', views.contacts_by_service, name='contacts_by_service'),
    path('contacts-by-tag/<int:tag_id>/', views.contacts_by_tag, name='contacts_by_tag'),
    path('contacts-by-status/<int:status_id>/', views.contacts_by_status, name='contacts_by_status'),
    path('contacts-by-staff/<int:assigned_staff_id>/', views.contacts_by_assigned_staff, name='contacts_by_assigned_staff'),
    path('contacts-trafick-source/<int:traffic_source_id>/', views.contacts_by_traffic_source, name='contacts_by_traffic_source'),
    path('contact/', views.filter_contact, name='filter_contact'),
    path('contact-query/', views.search_contact, name='search_contact'),



    # path('contacts/filter/<str:filter_type>/<int:filter_id>/', filter_contacts, name='filter_contacts'),
    path('contacts/<int:contact_id>/create-account/', views.create_user_account_for_contact, name='create_user_account_for_contact'),
    path('delete-contact/<int:contact_id>/delete', views.delete_contact, name='delete_contact'),
    path('update-contact/<int:contact_id>/update', views.update_contact, name='update_contact'),
    path('contact_deatil/<int:contact_id>/', views.contact_detail, name='contact_detail'),
    path('add-contact', views.create_contact, name='add_contact'),
    path("assigned-contacts/", views.my_assigned_contacts, name='my_assigned_contacts'),
    path("contact-list/", views.contact_list, name='contact_list'),

    path("contacts-bulk-action/", views.contacts_bulk_action, name='contacts_bulk_action'),

    #Statuses
    path('status-list', views_status.status_list, name='status_list'),
    path('edit-status/<int:status_id>/', views_status.edit_status, name='edit_status'),
    path('delete-status/<int:status_id>/', views_status.delete_status, name='delete_status'),


    #Tags
    path('tag-list', views_tags.tag_list, name='tag_list'),
    path('edit-tag/<int:tag_id>/', views_tags.edit_tag, name='edit_tag'),
    path('delete-tag/<int:tag_id>/', views_tags.delete_tag, name='delete_tag'),

    #Imports
    #Tags
    path('import-contact', views_import.import_contacts, name='import_contacts'),
    path('map_fields/', views_import.map_fields, name='map_fields'),
    path('save_mapped_data/', views_import.save_mapped_data, name='save_mapped_data'),
]



