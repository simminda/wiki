from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # search needs to come before the catch-all pattern
    path("search/", views.search, name="search"),
    path("random/", views.random_entry, name="random_entry"),
    path("create/", views.create_new_entry, name="create"),
    path("wiki/<str:title>/edit", views.edit_entry, name="edit_entry"),
    path("wiki/<str:title>/delete", views.delete_entry, name="delete_entry"),
    # catch-all pattern needs to be at the end
    path("<str:title>", views.entry, name="entry"),
]
