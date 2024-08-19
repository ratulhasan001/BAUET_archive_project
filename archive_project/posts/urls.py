from . import views
from django.urls import path

urlpatterns = [
    path('add/', views.add_post, name = 'add_post'),
    path('edit/<int:id>', views.edit_post, name = 'edit_post'),
    path('details/<int:id>/', views.DetailPostView.as_view(), name='detail_post'),
    path('delete/<int:id>', views.delete_post, name = 'delete_post'),
     path('add_to_wishlist/<int:post_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:post_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
