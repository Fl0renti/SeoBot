from django.urls import path
from .views import CreateAccessUser, PasswordChangeView, password_success, UsersListView, UserDeleteView, UserUpdateView    

app_name = 'accounts'
urlpatterns = [
    path("access_user/", CreateAccessUser.as_view(), name="access_user"),
    path("password/", PasswordChangeView.as_view(), name="change_password"),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="delete_user"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="update_user"),
]  