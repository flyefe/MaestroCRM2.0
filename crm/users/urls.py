from django.urls import path
# from . import views

# from .views import change_password, users_bulk_action, users_table, edit_user, register_user, create_group, users_in_group, delete_user, edit_group, delete_group
from . import views

#Users
urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('add-staff/', views.add_staff_user, name='add_staff_user'),
    path("users/", views.users_table, name='user_list'),
    path("staffs/", views.staff_table, name='staff_list'),
    path("edit-user/<int:user_id>/", views.edit_user, name='edit_user'),
    path("change-password/<int:user_id>/", views.change_password, name='change_password'),
    path("users-bulk-action/", views.users_bulk_action, name='users_bulk_action'),

    path("edit-role/<int:group_id>/", views.edit_group, name='edit_group'),
    path("delete-role/<int:group_id>/", views.delete_group, name='delete_group'),
    path("create_role/", views.create_group, name='create_group'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('group/<int:group_id>/users/', views.users_in_group, name='users_in_group'),
    # path("accounts/login/", login_view, name='admin-login'),
    # path("accounts/login/registration", login_view, name='admin-login'),
    # path("accounts/logout/", logout_view, name='logout'),
]