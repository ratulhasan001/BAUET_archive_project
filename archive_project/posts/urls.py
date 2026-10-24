from django.urls import path

from . import views

urlpatterns = [
    path("add/", views.add_post, name="add_post"),
    path("details/<int:id>/", views.detail_post, name="detail_post"),
    path("edit/<int:id>/", views.edit_post, name="edit_post"),
    path("delete/<int:id>/", views.delete_post, name="delete_post"),
    path("add_to_wishlist/<int:post_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("remove_from_wishlist/<int:post_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
]
