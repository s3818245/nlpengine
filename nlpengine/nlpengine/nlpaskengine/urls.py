from multiprocessing.forkserver import connect_to_new_process
from tkinter import N
from django.urls import path
from . import views
urlpatterns = [
    path('query/', views.get_query, name="query"),
    path('database/connect/', views.connect_database, name="database_connect"),
    path('database/disconnect/', views.disconnect_database, name = "db_disconnect"),
    path('database/get/', views.get_metadata, name="metadata"),
    path('query/keyword/', views.get_keyword_type, name="keyword")
]